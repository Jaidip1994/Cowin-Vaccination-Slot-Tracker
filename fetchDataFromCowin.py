import datetime
import requests
import json
import argparse
import sys
import pandas as pd

current_date = datetime.datetime.now().strftime("%d-%m-%Y")
FEE_TYPE = { 'p' : 'Paid', 'f' : 'Free', 'a' : 'All'}
KEYS_LIST = ['center_id','name', 'district_name', 'block_name', 'pincode', 'from', 'to', 'fee_type', 'a45', 'b45']
SESSIONS_LIST = ['date', 'available_capacity', 'vaccine', 'available_capacity_dose1', 'available_capacity_dose2', 'min_age_limit']
VACCINE_FEE = ['vaccine', 'fee']

def _url(path:str):
    return 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/' + path

def _fetch_slots_by_date_district(districtCode: str, date :str):
    print('Refreshing Data')
    url = f"calendarByDistrict?district_id={districtCode}&&date={date}"
    response = requests.request("GET", _url(url))
    if response.status_code != 200:
        return None
    return json.loads(response.text)
 
parser = argparse.ArgumentParser(description="Vaccination Tracker" ,
                                 epilog='Enjoy the program! :)' )
parser.add_argument('DistrictCode',
                       metavar='-d',
                       type=str,
                       help='District Code details', default= 730)

args = parser.parse_args()
districtCode = args.DistrictCode

fetchVaccinationData = _fetch_slots_by_date_district(districtCode, current_date)
if not fetchVaccinationData:
    print('No Vaccination Details Found ...')
    sys.exit()

def fetchAndStoreDataFromCowin():
    final_list_of_hospital = []
    final_slots_per_center = dict()
    final_fee_per_hospital = dict()
    pincode_dose_wise_count = {'firstDose' : [], 'secondDose': [] }
    vaccine_names = set()
    for centerData in fetchVaccinationData['centers']:
        temp_data =  { key : value for key, value in centerData.items() if key in KEYS_LIST}
        session_list = []
        temp_data['b45'] = False
        temp_data['a45'] = False
        for session in centerData['sessions']:
            temp_session_data = { key : value for key, value in session.items() if key in SESSIONS_LIST}
            if temp_session_data['available_capacity_dose1'] > 0 and temp_data['pincode'] not in pincode_dose_wise_count['firstDose']:
                pincode_dose_wise_count['firstDose'].append(temp_data['pincode'])
            if temp_session_data['available_capacity_dose2'] > 0 and temp_data['pincode'] not in pincode_dose_wise_count['secondDose']:
                pincode_dose_wise_count['secondDose'].append(temp_data['pincode'])
            vaccine_names.add(temp_session_data['vaccine'])
            if temp_session_data['min_age_limit'] == 18:
                temp_data['b45'] = True
            else:
                temp_data['a45'] = True
            session_list.append(temp_session_data)
        if session_list:
            final_slots_per_center[centerData[KEYS_LIST[0]]] = session_list
            final_list_of_hospital.append(temp_data)
            if centerData['fee_type'] == 'Paid':
                final_fee_per_hospital[centerData[KEYS_LIST[0]]] = centerData['vaccine_fees']
    df = pd.DataFrame.from_dict(final_list_of_hospital)
    df.to_csv("./output_file/hospitaldata.csv", index=False)
    dict_with_hospital_data = {}
    dict_with_hospital_data['slots_per_hospital'] = final_slots_per_center
    dict_with_hospital_data['fee_per_hospital'] = final_fee_per_hospital
    dict_with_hospital_data['pincode_dose_wise_count'] = pincode_dose_wise_count
    dict_with_hospital_data['dict_with_hospital_data'] = list(vaccine_names)
    with open('./output_file/few_more_details.json', 'w') as fp:
        json.dump(dict_with_hospital_data, fp)


def _proccess_per_age(center_id, df_per_age, age_slot, final_fee_per_hospital, df, available_slots, vaccine_type = None):
    dose1_df = df_per_age[df_per_age['available_capacity_dose1'] > 0]
    dose2_df = df_per_age[df_per_age['available_capacity_dose2'] > 0]
    message_string = None

    if not dose1_df.empty and vaccine_type:
        dose1_df = dose1_df[dose1_df['vaccine'] == vaccine_type]
    if not dose2_df.empty and vaccine_type:
        dose2_df = dose2_df[dose2_df['vaccine'] == vaccine_type]

    if not dose1_df.empty or not dose2_df.empty:
        hospital_data = df[df['center_id'] == center_id].copy()
        message_string = f'[{age_slot}][{hospital_data.pincode.values[0]}]\n\n'
        message_string += f'District Name: *{hospital_data.district_name.values[0]}*\n'
        message_string += f'Age: *{age_slot}*\n'
        message_string += f'Pincode: *{hospital_data.pincode.values[0]}*\n'
        message_string += f'Name: *{hospital_data.name.values[0]}*\n'
        message_string += f'Fee: *{hospital_data.fee_type.values[0]}*\n'
        if (hospital_data.fee_type == 'Paid').values[0]:
            amount = final_fee_per_hospital[str(center_id)][0]['fee']
            message_string += f'Amount: *{amount}*\n'

    if not dose1_df.empty:
        vaccine_name = dose1_df['vaccine'].unique()[0]
        message_string += f'Vaccine Name: *{vaccine_name}*\n'
        for index, row in dose1_df.iterrows():
            message_string += f'{row.date} : Total *{row.available_capacity_dose1}* Slots ( 1st Dose )\n'

    if not dose2_df.empty:
        if dose1_df.empty:
            vaccine_name = dose2_df['vaccine'].unique()[0]
            message_string += f'Vaccine Name: *{vaccine_name}*\n'
        for index, row in dose2_df.iterrows():
            message_string += f'{row.date} : Total *{row.available_capacity_dose2}* Slots ( 2nd Dose )\n'

    if message_string:
        available_slots.append(message_string)


def dose_processing(center_id_with_slot, final_fee_per_hospital, df, vaccine_type = None):
    available_slots = []
    for key, value in center_id_with_slot.items():
        temp_df = pd.DataFrame.from_dict(value)
        _proccess_per_age(int(key), temp_df[temp_df['min_age_limit'] == 18], 18, final_fee_per_hospital, df, available_slots, vaccine_type)
        _proccess_per_age(int(key), temp_df[temp_df['min_age_limit'] == 45], 45, final_fee_per_hospital, df, available_slots, vaccine_type)
    return available_slots