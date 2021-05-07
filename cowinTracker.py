# https://www.pushbullet.com/#people

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import datetime
from win10toast import ToastNotifier
import requests
import json
import pprint
from alive_progress import alive_bar

PINCODE_LIST = ["560066", "560020", "560037", "560030", "560011", "560078", "560017", "560084" ]
TOKEN = 'o.maWrkwmNzKLIoN0AgsChj95xdtiMXX3G'
WHATSGRPORPERSONNAME = 'Sashu'

def pushbullet_message(body):
    msg = { "type" : "note", "title" : "Available Slots", "body": body}
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                        data=json.dumps(msg),
                        headers={'Authorization': 'Bearer ' + TOKEN,
                                'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)
    else:
        print ('Message sent')

def messageParse(dict_val):
    final_message = ""
    for key, value in dict_val.items():
        final_message += f'Hospital Name is {key} \n Pincode: {value["pincode"]} \n Availaibility on \n'
        for date, availability in value["slots"].items():
            # TODO :Tweak here
            if date != '' and availability[0] not in ['Booked', 'NA']:
                final_message += f'\t {date} -> No. {availability[0]}, Age {availability[1]} \n'
        final_message += f'\n'
    return final_message
count = 1
driver = webdriver.Chrome("utility\chromedriver.exe")
driver.get("https://web.whatsapp.com/")
driver.maximize_window()
time.sleep(10)
while True:
    print(f"Trying for {count} Times")
    driver.get("https://www.cowin.gov.in/home")
    availableHospital = {}
    with alive_bar(len(PINCODE_LIST)) as bar:
        for indpincode in PINCODE_LIST:
            bar()
            pincode = driver.find_element_by_xpath("//input[@data-placeholder='Enter your PIN']")
            pincode.clear()
            pincode.send_keys(indpincode)
            pincode.send_keys(Keys.ENTER)
            time.sleep(3)
            # Age 18+ Check Box
            driver.find_element_by_xpath("//label[contains(text(),'18')]").click()

            datedetails = driver.find_elements_by_xpath("//slide//p")
            datelist = [datedetail.text for datedetail in datedetails]

            hospital_names = driver.find_elements_by_xpath("//span[contains(@class, 'paid-button')]/..")
            hospital_names_list = [hospitalname.text for hospitalname in hospital_names]
            for index, hospital_name in enumerate(hospital_names_list):
                # get just paid
                value = driver.find_elements_by_xpath(f"(//span[contains(@class, 'paid-button')])[{index+1}]/../../../../div[last()]//li//div[contains(@class,'slots-box')]//a")    
                # get all
                # value = driver.find_elements_by_xpath(f"(//h5[contains(@class, 'center-name')])[{index+1}]/../../../div[last()]//li//div[contains(@class,'slots-box')]//a")    
                valueToConsider = False
                countList = []
                agebracket = []
                for linkindex, link in enumerate(value):
                    # TODO :Tweak here
                    if link.text.isdigit():
                        valueToConsider = True
                    if link.text != 'NA':    
                        age = driver.find_element_by_xpath(f"((//span[contains(@class, 'paid-button')])[{index+1}]/../../../../div[last()]//li//div[contains(@class,'slots-box')]//a)[{linkindex + 1}]/../div/span")    
                    else: 
                        age = None
                    countList.append(link.text)
                    agebracket.append(age.text if age is not None else age)     
                if not valueToConsider:
                    continue
                availableHospital[hospital_name] = { 'slots' : dict(zip(datelist, zip(countList, agebracket))) }
                availableHospital[hospital_name].update({"pincode" : indpincode}) 
    

    if bool(availableHospital):
        today = datetime.datetime.now()
        hr = ToastNotifier()
        hr.show_toast("Hospital Slots Available", ", ".join(list(availableHospital.keys())))
        pushbullet_message(messageParse(availableHospital))
        # pywhatkit.sendwhatmsg('+918777621918', messageParse(availableHospital), datetime.datetime.now().hour, datetime.datetime.now().minute + 2 )
        driver.get("https://web.whatsapp.com/")
        time.sleep(15)
        driver.find_element_by_xpath(f'//span[@title=\'{WHATSGRPORPERSONNAME}\']/../../..').click()
        inp_xpath = "//footer/..//div[@contenteditable='true']"
        input_box = driver.find_element_by_xpath(inp_xpath)
        input_box.send_keys("Hospital Slots Available ", ", ".join(list(availableHospital.keys())))
        input_box.send_keys(Keys.ENTER)
    time.sleep(5)            

    # pprint.pprint(availableHospital)
    print("Will Try after 10mins...")
    time.sleep(600)
    count+=1

