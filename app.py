import streamlit as st
from simpledbf import Dbf5
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def bp_check(bp_value_str):
    try:
        sys, dia = map(int, bp_value_str.split('/'))
        if sys <= 139 and dia <= 89:
            return 'Normal_BP'
        else:
            return 'Abnormal_BP'
    except:
        pass

def bmi_check(BMI):
    if BMI < 18.50:
        return 'underweight'
    elif BMI > 24.90 and BMI < 30.0:
        return 'overweight'
    elif BMI > 30.0:
        return 'obese'


def vision_check(remark):
    if 'EYE' in remark:
        return 'Abnormal vision'
# def vision_check(vision_values):
#     if '6/12' in vision_values.values:
#         return True


def ecg_check(remark):

    if 'ECG' in remark:
        return 'Total'
    # if 'ECG>REF' in remark or 'ECG REF' in remark or 'REF ECG' in remark:
    #     return 'Referred'
    # elif 'REFUSE ECG' in remark.upper() or 'REFUSE>ECG' in remark.upper():
    #     return 'Refused'
    # else:
    #     return 'Normal'

def waist_check(sex, waist):
    if sex == 2 and waist > 80:
        return 'Abnormal_waist_female'
    if sex == 1 and waist > 90:
        return 'Abnormal_waist_male'

def convert_bytes_to_df(bytes_data):
    # Write bytes to a .dbf file
    with open('temp.dbf', 'wb') as file:
        file.write(bytes_data)

    # Convert .dbf file to DataFrame
    dbf = Dbf5('temp.dbf')
    df = dbf.to_dataframe()

    return df

def analyze(df):
    # df = Dbf5(dbf_path).to_dataframe()
    df['REMARKS'] = df['REMARKS'].astype(str)
    report = {}
    report['site'] = df['HTH_CENTRE'][0]
    report['total_screened'] = len(df)
    report['sex_stats'] = df['SEX'].replace({2: 'Female', 1: 'Male'}).value_counts().to_dict()
    BP_retakes = df['BP_2ND'].notna().sum()
    report['BP_retakes'] = BP_retakes
    report['BP_retake_stats'] = df.apply(lambda x: bp_check(x['BP_2ND']), axis=1).value_counts().to_dict()
    report['BMI_stats'] = df.apply(lambda x: bmi_check(x['BMI']), axis=1).value_counts().to_dict()
    report['waist_stats'] = df.apply(lambda x: waist_check(x['SEX'], x['WAIST']), axis=1).value_counts().to_dict()
    report['ECG_stats'] = df[df['REMARKS'].str.contains('ECG')]['REMARKS'].apply(ecg_check).value_counts().to_dict()
    # report['abnormal_vision'] = df[['VISION_RT', 'VISION_LT']].apply(vision_check, axis = 1).sum()
    report['Vision_stats'] = df[df['REMARKS'].str.contains('EYE')]['REMARKS'].apply(vision_check).value_counts().to_dict()
    report['HBA1C_refused'] = df[df['HAEMOCUE'] >= 7]['REMARKS'].str.upper().str.contains('REFUSE').sum()
    report['follow_ups'] = df['PREV_RX'].astype(str).str.contains('HBP|CHD|CARDIAC').sum()
    # report['follow_ups'] = df['PREV_RX'].astype(str).apply(lambda x: 'CHD' in x).sum()
    report['ECG_stats'] = df[df['REMARKS'].str.contains('ECG')]['REMARKS'].apply(ecg_check).value_counts().to_dict()

    return report



if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.header('Magic Data Analyzer')
    
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    

    
    for files in uploaded_files:
        bytes_data = files.getvalue()
        df = convert_bytes_to_df(bytes_data)
        with st.expander(f'View File {files.name}'):
            st.dataframe(df)
        
        report = analyze(df)
        
        st.write(report)


 
        
        
        st.write('-----')
        
        # report = analyze(bytes_data)
