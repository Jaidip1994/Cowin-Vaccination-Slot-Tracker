import os
import telebot
from dotenv import load_dotenv
import fetchDataFromCowin as fd
import pandas as pd
import json
import time

project_folder = os.path.expanduser('./utility')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode= 'markdown')


@bot.message_handler(commands=['start'])
def hello(message):
    while True:
        fd.fetchAndStoreDataFromCowin()
        with open('./output_file/few_more_details.json') as fp:
            dict_with_hospital_data = json.load(fp)

        final_slots_per_center = dict_with_hospital_data['slots_per_hospital']
        final_fee_per_hospital = dict_with_hospital_data['fee_per_hospital']
        pincode_dose_wise_count = dict_with_hospital_data['pincode_dose_wise_count']
        vaccine_names = dict_with_hospital_data['dict_with_hospital_data']
        df = pd.read_csv('./output_file/hospitaldata.csv')
        available_slots = fd.dose_processing(
            final_slots_per_center, final_fee_per_hospital, df)
        print(len(available_slots))
        print(message.chat.id)
        for msg in available_slots:
            bot.send_message(message.chat.id, msg)
        print("Will Try after 10Sec...")
        time.sleep(60)    

bot.polling()
