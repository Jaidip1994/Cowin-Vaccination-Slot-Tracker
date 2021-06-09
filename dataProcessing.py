import json
import pandas as pd

with open('./output_file/few_more_details.json') as fp:
    dict_with_hospital_data = json.load(fp)

final_slots_per_center = dict_with_hospital_data['slots_per_hospital']
final_fee_per_hospital = dict_with_hospital_data['fee_per_hospital']
# pincode_dose_wise_count = dict_with_hospital_data['pincode_dose_wise_count']
# vaccine_names = dict_with_hospital_data['dict_with_hospital_data']
df = pd.read_csv('./output_file/hospitaldata.csv')
available_slots = []


def _proccess_per_age(center_id, df_per_age, age_slot, final_fee_per_hospital, df):
    dose1_df = df_per_age[df_per_age['available_capacity_dose1'] > 0]
    dose2_df = df_per_age[df_per_age['available_capacity_dose2'] > 0]
    message_string = None
    if not dose1_df.empty or not dose2_df.empty:
        hospital_data = df[df['center_id'] == center_id].copy()
        print(hospital_data.shape)
        message_string = f'[{age_slot}][{hospital_data.pincode.values[0]}]\n\n'
        message_string += f'District Name: **{hospital_data.district_name.values[0]}**\n'
        message_string += f'Age: **{age_slot}**\n'
        message_string += f'Pincode: **{hospital_data.pincode.values[0]}**\n'
        message_string += f'Name: **{hospital_data.name.values[0]}**\n'
        message_string += f'Fee: **{hospital_data.fee_type.values[0]}**\n'
        if (hospital_data.fee_type == 'Paid').values[0]:
            amount = final_fee_per_hospital[str(center_id)][0]['fee']
            message_string += f'Amount: **{amount}**\n'

    if not dose1_df.empty:
        vaccine_name = dose1_df['vaccine'].unique()[0]
        message_string += f'Vaccine Name: **{vaccine_name}**\n'
        for index, row in dose1_df.iterrows():
            message_string += f'{row.date} : Total **{row.available_capacity_dose1}** Slots ( 1st Dose )\n'

    if not dose2_df.empty:
        if dose1_df.empty:
            vaccine_name = dose2_df['vaccine'].unique()[0]
            message_string += f'Vaccine Name: **{vaccine_name}**\n'
        for index, row in dose2_df.iterrows():
            message_string += f'{row.date} : Total **{row.available_capacity_dose2}** Slots ( 2nd Dose )\n'

    if message_string:
        available_slots.append(message_string)


def dose_processing(center_id_with_slot, final_fee_per_hospital, df):
    for key, value in center_id_with_slot.items():
        temp_df = pd.DataFrame.from_dict(value)
        _proccess_per_age(int(key), temp_df[temp_df['min_age_limit'] == 18], 18, final_fee_per_hospital, df)
        _proccess_per_age(int(key), temp_df[temp_df['min_age_limit'] == 45], 45, final_fee_per_hospital, df)
    return available_slots

# dose_processing(final_slots_per_center, final_fee_per_hospital)
# print(len(final_slots_per_center))
