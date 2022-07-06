from dotenv import load_dotenv
from pathlib import Path
import os
import json
import requests
from jsontodf.transform import * 
import numpy as np


def get_jsons_from_strapi(id1, id2): 
    headers = get_header()
    print(headers)
    url = "https://sociogram-api.braveup.co/survey-pre-analityc-formats/"+str(id1)
    payload={}

    response = requests.request("GET", url, headers=headers)
    query1 = json.loads(response.text)
    df1 = transform(query1['content'])
    
    url = "https://sociogram-api.braveup.co/survey-pre-analityc-formats/"+str(id2)
    #payload={}

    response = requests.request("GET", url, headers=headers)
    query2 = json.loads(response.text)
    df2 = transform(query2['content'])
    return df1, df2

def get_total_nets_changes(df1, df2, id_question_net_0=5, id_question_net_1=36):
    df1_test = df1[df1['question_id']==id_question_net_0]
    df1_test['response_content'] = df1_test['response_content'].astype(str) 
    df1_test['arc'] = df1_test[['name', 'response_content']].agg('-'.join, axis=1)
    df1_test['arc'] = df1_test['arc'].str.lower()
    df1_test['arc'] = df1_test['arc'].replace(' ', '')

    df_test = df2[df2['question_id']==id_question_net_1]
    df_test['response_content'] = df_test['response_content'].astype(str) 
    df_test['arc'] = df_test[['name', 'response_content']].agg('-'.join, axis=1)
    df_test['arc'] = df_test['arc'].str.lower()
    df_test['arc'] = df_test['arc'].replace(' ', '')

    percent_maintain = np.round(sum(df1_test['arc'].isin(df_test.arc.to_list()))/len(df1_test['arc']),2)
    percent_new = np.round(sum(~df_test['arc'].isin(df1_test.arc.to_list()))/len(df1_test['arc']),2)
    percent_lost = np.round(sum(~df1_test['arc'].isin(df_test.arc.to_list()))/len(df1_test['arc']),2)

    return {'mantain': percent_maintain, ' new': percent_new, ' lost': percent_lost}

def get_arcs_delta(df1, df2, id_question_0=5, id_question_1=36):
    df1_count = df1[df1.question_id==id_question_0][['name','answerId']].groupby('name').count().reset_index()
    df2_count =  df2[df2.question_id==id_question_1][['name','answerId']].groupby('name').count().reset_index()
    df2_count['shift_mean'] = df2_count['answerId'] - np.round(df2_count['answerId'].mean())
    df_consolidated = df1_count.merge(df2_count, on='name')
    df_consolidated.columns = ['name', '2021_friend_arcs', '2022_friend_arcs', 'shift_mean']
    df_consolidated['delta'] = df_consolidated['2022_friend_arcs']- df_consolidated['2021_friend_arcs']
    return df_consolidated

def add_feeling_questions_json(df2, df_consolidated, id_feeling_1=44, id_feeling_2=45):
    df2_feel1 = df2[df2.question_id==id_feeling_1][['name','Answers']]
    df2_feel1.columns = ['name', 'feel1']
    df_consolidated = df_consolidated.merge(df2_feel1, on='name')
    df2_feel2 = df2[df2.question_id==id_feeling_2][['name','Answers']]
    df2_feel2.columns = ['name', 'feel2']
    df_consolidated = df_consolidated.merge(df2_feel2, on='name')
    return df_consolidated.sort_values('delta').to_json(orient = 'records',force_ascii=False), df_consolidated

def get_header():
    dotenv_path = Path(".env")
    load_dotenv(dotenv_path=dotenv_path)
    USER = os.getenv("USERSTRAPI")
    PASSWORD = os.getenv("PASSWORD")
    AUTH = os.getenv("AUTH")

    url = "http://api.braveup.co/accounts/signin"
    payload = json.dumps({
    "email": USER,
    "password": PASSWORD
    })
    headers = {
    'Authorization': AUTH, 
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

    json.loads(response.text)['idToken']

    headers = {}
    headers['Authorization'] = 'Bearer '+json.loads(response.text)['idToken']
    headers['Content-Type'] = 'application/json'    
    return headers 
