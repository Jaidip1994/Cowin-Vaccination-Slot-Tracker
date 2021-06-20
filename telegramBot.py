import os
import telebot
from dotenv import load_dotenv
import fetchDataFromCowin as fd
import pandas as pd
import json
import time
import os

project_folder = os.path.expanduser('./utility')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode= 'markdown')

def cleanup_dir():
    print("... Cleaning Directory ...")
    dir = './output_file'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

def fetch_available_slots(vaccine_type = None):
    cleanup_dir()
    fd.fetchAndStoreDataFromCowin()
    with open('./output_file/few_more_details.json') as fp:
        dict_with_hospital_data = json.load(fp)

    final_slots_per_center = dict_with_hospital_data['slots_per_hospital']
    final_fee_per_hospital = dict_with_hospital_data['fee_per_hospital']
    pincode_dose_wise_count = dict_with_hospital_data['pincode_dose_wise_count']
    vaccine_names = dict_with_hospital_data['dict_with_hospital_data']
    df = pd.read_csv('./output_file/hospitaldata.csv')
    return fd.dose_processing(
        final_slots_per_center, final_fee_per_hospital, df, vaccine_type)


@bot.message_handler(commands=['start'])
def hello(message):
    while True:
        available_slots = fetch_available_slots()
        print(f'Message Id: {message.chat.id} Available Number of Slots {len(available_slots)}')
        for msg in available_slots:
            bot.send_message(message.chat.id, msg)
        print(f"Message {message.chat.text} Will Try after 10Sec...")
        time.sleep(60)    

@bot.message_handler(commands=['covaxin'])
def fetch_all_covaxin(message):
    available_slots = fetch_available_slots('COVAXIN')
    print(f'Message Id: {message.chat.id} Available Number of Slots {len(available_slots)}')
    for msg in available_slots:
        bot.send_message(message.chat.id, msg)
    print(f"Message {message.chat} Will Try after 10Sec...")
    time.sleep(60)  

bot.polling()
