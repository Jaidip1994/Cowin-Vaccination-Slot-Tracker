import requests
import datetime
import json
import argparse
import pprint
import sys
from selenium.webdriver.common import keys
import streamlit as st
import pandas as pd
import json

# streamlit run C:\Users\jaidi\OneDrive\Documents\Development_Code\Python\CowinTracker\Cowin-Vaccination-Slot-Tracker\cowinTrackerOpenApi.py 730

pd.options.display.max_columns = 50

current_date = datetime.datetime.now().strftime("%d-%m-%Y")
FEE_TYPE = { 'p' : 'Paid', 'f' : 'Free', 'a' : 'All'}
KEYS_LIST = ['center_id','name', 'district_name', 'block_name', 'pincode', 'from', 'to', 'fee_type', 'a45', 'b45']
SESSIONS_LIST = ['date', 'available_capacity', 'vaccine', 'available_capacity_dose1', 'available_capacity_dose2', 'min_age_limit']
VACCINE_FEE = ['vaccine', 'fee']

def _url(path:str):
    return 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/' + path

def fetch_slots_by_date_district(districtCode: str, date :str):
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
                       help='District Code details')

args = parser.parse_args()
districtCode = args.DistrictCode

final_list_of_hospital = []
final_slots_per_center = dict()
final_fee_per_hospital = dict()

fetchVaccinationData = fetch_slots_by_date_district(districtCode, current_date)
if not fetchVaccinationData:
    print('No Vaccination Details Found ...')
    sys.exit()

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
with open('./output_file/slots_per_hospital.json', 'w') as fp:
    json.dump(final_slots_per_center, fp)
with open('./output_file/fee_per_hospital.json', 'w') as fp:
    json.dump(final_fee_per_hospital, fp)
pincode_list = df['pincode'].unique()

def format_func(option, feetype, min_age_limit):
    temp_df = df[(df['pincode']==option)].copy()
    if min_age_limit == 18:
        temp_df = temp_df[temp_df['b45']==True]
    elif min_age_limit == 45:
        temp_df = temp_df[temp_df['a45']==True]
    if feetype:
        temp_df = temp_df[temp_df['fee_type'] == feetype ]
    temp_df.reset_index(inplace=True)
    return temp_df.iloc[:,1:]

def provideSlots(center_id, min_age_limit, vaccine_name):
    temp_df = pd.DataFrame.from_dict(final_slots_per_center[center_id])
    if min_age_limit:
        temp_df = temp_df[temp_df['min_age_limit'] == min_age_limit ]
    temp_df = temp_df[temp_df['vaccine'] == vaccine_name]
    return temp_df

def provide_fees_details(center_id, vaccine_name):
    temp_dict = final_fee_per_hospital[center_id] if center_id in list(final_fee_per_hospital.keys()) else dict()
    temp_dict = { elem['vaccine']:elem['fee']  for elem in temp_dict if elem['vaccine'] == vaccine_name }
    return temp_dict


st.title("List of Hospitals Providing Covid Vaccination in Kolkata Region (WB)")
st.header("Input Details")
st.write("Do you need details, where Dosages is available or all, Please provide your choice ? ")

dosageType = st.radio("Choice", ['First Dosage', 'Second Dosage', 'Both'])

if dosageType == 'First Dosage':
    pincode_list = pincode_dose_wise_count['firstDose']
elif dosageType == 'Second Dosage':
    pincode_list = pincode_dose_wise_count['secondDose']

st.markdown("Please Provide the below Details")
column = st.selectbox("Pincode List", pincode_list)
feetype = st.selectbox("Fee Type", [None, 'Paid', 'Free'])
min_age_limit = st.selectbox("Minimum Age Limit",[None, 18, 45])

st.markdown("Hospital Names")
df_selected = format_func(column, feetype, min_age_limit)
st.dataframe(df_selected) 

centerId = st.selectbox("Select Center Id",df_selected.center_id.tolist())
vaccine_name = st.selectbox("Select Vaccine Name", list(vaccine_names))
st.write(provideSlots(centerId, min_age_limit, vaccine_name))
st.markdown('Fee Details')
st.write(provide_fees_details(centerId, vaccine_name))