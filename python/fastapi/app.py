import requests, json
from fastapi import FastAPI
from pymongo import MongoClient
import pandas as pd
import os.path
import xmltodict
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from models import Pyeup, PyeupApi
import uuid
# 그래프 import
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from dtaidistance import dtw
from flask import Flask, render_template


app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, '../../secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        errorMsg = "Set the {} environment variable.".format(setting)
        return errorMsg

HOSTNAME = get_secret("Local_Hostname")
USERNAME = get_secret("Local_Username")
PASSWORD = get_secret("Local_Password")

APIKEY = get_secret("API_KEY")

PORT = get_secret("Mysql_Port")
SQLUSERNAME = get_secret("Mysql_Username")
SQLPASSWORD = get_secret("Mysql_Password")
SQLDBNAME = get_secret("Mysql_DBname")

TEAMHOSTNAME = get_secret("My_Team_Hostname")


DB_URL = f'mysql+pymysql://{SQLUSERNAME}:{SQLPASSWORD}@{HOSTNAME}:{PORT}/{SQLDBNAME}'

class db_conn:
    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle=500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
    
    def connection(self):
        conn = self.engine.connection()
        return conn

url = 'http://0.0.0.0:5500/shoppingmall_closed'  # 5000번 포트에서 가져올게요
response = requests.get(url)
json_data = response.json()

client = MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}')

db = client['api_pj']
col = db['shoppingmall_closed']

sqldb = db_conn()
session = sqldb.sessionmaker()

# 포트 연결 확인용
@app.get(path='/')
async def connectionCheck():
    return "connected"

# 연도별 폐업한 업종의 수와 증감률 계산하기
@app.get(path='/mongoYear')
async def mongoYear():
    col = db['shppingmall_year_count']
    data1 = list(col.find({},{"_id":0}))
    if len(data1) != 0:
        return {"result code":200, "result":data1}
    else:
        new_df = pd.DataFrame(columns=['year','subject', 'count', 'percentage'])
        # 2019~2023 까지 반복
        for year in range(2019,2024):
            data = await calc(year) # 이번년도 데이터
            last_data = await calc(year-1) # 작년도 데이터

            # 각 항목별 카운트 값을 구한다.
            column_dict = {'교육/도서/완구/오락':0, '가전':0, '컴퓨터/사무용품':0, '가구/수납용품':0, '건강/식품':0, '의류/패션/잡화/뷰티':0, '자동차/자동차용품':0, '레져/여행/공연':0, '기타':0}
            last_column_dict = {'교육/도서/완구/오락':0, '가전':0, '컴퓨터/사무용품':0, '가구/수납용품':0, '건강/식품':0, '의류/패션/잡화/뷰티':0, '자동차/자동차용품':0, '레져/여행/공연':0, '기타':0}

            # 이번년도 모든 데이터 순회
            for i in range(0, len(data)):
                subject_val = data.iloc[i,1]
                for j in column_dict:
                    if j in subject_val:
                        column_dict[j] += 1
            for i in range(0, len(last_data)):
                last_subject = last_data.iloc[i,1]
                for i in column_dict:
                    if i in last_subject:
                        last_column_dict[i] += 1
            # 증감률을 구한다. (이번년도 데이터 - 작년 데이터) / 작년 데이터 * 100), 소수점은 첫째 자리까지만 구한다.
            result_dict = {key: round(((column_dict[key] - last_column_dict[key]) / last_column_dict[key]) * 100, 1) for key in column_dict}
            
            # 새로운 행 추가
            for key, value in column_dict.items():
                new_row = pd.DataFrame({'year': year,'subject': key, 'count': value, 'percentage': result_dict[key]}, index=[0])
                new_df = pd.concat([new_df, new_row], ignore_index=True)

        new_df = new_df.drop_duplicates()
        data_dict_list = new_df.to_dict(orient='records')
        col.insert_many(data_dict_list)
        data1 = list(col.find({},{"_id":0}))
        return {"result code":200, "result":data1}

# year를 인자로 받아 해당 인자와 동일한 행만 가져오기
@app.get(path='/calc')
async def calc(year = None):
    cursor = col.find({}, { "_id":0})
    df = pd.DataFrame(list(cursor))
    df_cal = df.iloc[:,[1,8]]
    if year is None:
        df_calc = df_cal
    else:
        df_calc = df_cal.loc[(df_cal['폐업일자'].dt.year)==int(year)]
    return df_calc

# sql table에 데이터 삽입
@app.get('/insertSQL')
async def insertSQL():
    # year에 맞는 폐업데이터가 sql에 존재시 sql 데이터를  리턴
    result = session.query(Pyeup).all()
    if (len(result) != 0):
        return {"result code":200, "result":result}
    else:
        data = await mongoYear()
        data = list(data['result'])
        for item in data:
            new_pyeup = Pyeup(id=uuid.uuid4(), year=item['year'], subject=item['subject'], count=item['count'], percentage=item['percentage'])
            session.add(new_pyeup)
            session.commit()
            session.refresh(new_pyeup)
            result = session.query(Pyeup).all()
        
        return {"result code":200, "result":result}
    
#  공공데이터API에서 데이터를 가져오는 api
@app.get(path='/getApi')
async def getApi():
    url = 'http://www.localdata.go.kr/platform/rest/GR0/openDataApi'
    url += '?authKey=' + APIKEY
    url += '&state=03'

    response = requests.get(url)
    contents = response.text
    result = {"resultcode": response.status_code}
    json_data = xmltodict.parse(contents)
    # json_string = json.dumps(json_data, ensure_ascii=False)

    result['result'] = json_data['result']
    
    return result

# 데이터를 가져와서 mongoDB에 넣는 api
@app.get(path='/insertApiMongo')
async def insertApiMongo():
    response = await getApi()
    col = db['today_failed']
    col.insert_one(response)
    
    return col.find_one({},{"_id":0})

# mongo에 저장된 공공데이터 api 가져오기
@app.get(path='/getApiMongo')
async def getApiMongo():
    col = db['today_failed']
    data = col.find_one({},{"_id":0})
    
    if len(list(data)) == 0:
        data = await insertApiMongo()
    data_uptae = data['result']['body']['rows']['row']
    column_dict = {'교육/도서/완구/오락':0, '가전':0, '컴퓨터/사무용품':0, '가구/수납용품':0, '건강/식품':0, '의류/패션/잡화/뷰티':0, '자동차/자동차용품':0, '레져/여행/공연':0, '기타':0}
    today_failed = [item['uptaeNm'] for item in data_uptae]
    for i in column_dict:
        for j in today_failed:
            if i in j:
                column_dict[i] += 1
    return {"result code":200, "result":column_dict}


# sql table에 데이터 삽입
@app.get('/getPyeupApiSql')
async def insertApiSql():
    # year에 맞는 폐업데이터가 sql에 존재시 sql 데이터를  리턴
    result = session.query(PyeupApi).all()
    if (len(result) != 0):
        return {"result code":200, "result":result}
    else:
        data = await getApiMongo()
        data = data['result']
        for key, item in data.items():
            new_pyeup_api = PyeupApi(id=uuid.uuid4(), subject=key, count=item)
            session.add(new_pyeup_api)
            session.commit()
            session.refresh(new_pyeup_api)
            result = session.query(PyeupApi).all()
        return {"result code":200, "result":result}

@app.get('/getJikguMall')
async def getJikguMall():
    response = requests.get('http://'+TEAMHOSTNAME+":3000/usingData")
    response = response.json()
    response = response['result']

    pyeup_data = await insertSQL()
    pyeup_data = pyeup_data['result']
    
    print(pyeup_data[0].year)
    total_count = {2019: 0, 2020:0, 2021:0, 2022:0, 2023:0}
    for i in range(len(pyeup_data)):
        total_count[pyeup_data[i].year] += pyeup_data[i].count
    pyeup_value = list(total_count.values())
    #print(response[0].values())
    shopping_value = list(response[0].values())
    shopping_value.pop()

    year = [2019,2020,2021,2022,2023]
    year =  np.array(year)
    shopping_value = np.array(shopping_value)
    pyeup_value = np.array(pyeup_value)
    pyeup_value = (pyeup_value/pyeup_value.sum()) * 100
    shopping_value = (shopping_value/shopping_value.sum()) * 100

    plt.rcParams['font.family'] = 'NanumBarunGothic'
    plt.bar(year-0.17, pyeup_value, 0.35,  label="폐업")
    plt.bar((year + 0.18),shopping_value, 0.35 , label="직구")
    plt.title("연도별 직구수와 폐업수")
    plt.xlabel('year')
    plt.legend()
    plt.savefig('../../front/public/bar_chart.png')
    return 0

#mongo data delete
@app.get(path='/datasetDelete')
async def deleteData():
    col.delete_many({})
    return "deleted"

