import requests, json
from fastapi import FastAPI
from pymongo import MongoClient
import pandas as pd
import os.path
import xmltodict

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

url = 'http://0.0.0.0:5500/shoppingmall_closed'  # 5000번 포트에서 가져올게요
response = requests.get(url)
json_data = response.json()

client = MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}')

db = client['api_pj']
col = db['shoppingmall_closed']

@app.get(path='/')
async def connectionCheck():
    return "connected"

@app.get(path='/onlinemalls')
async def onlinemalls():
    result = {"resultcode": response.status_code}
    data = list(col.find({}, {"_id": 0}))
    result['result'] = data
    return len(data)

@app.get(path='/calc')
async def divideSection(year = None, subject=None):
    cursor = col.find({}, { "_id":0})
    df = pd.DataFrame(list(cursor))
    print(df.columns)
    df_cal = df.iloc[:,[1,8]]
    df_calc = df_cal.loc[((df_cal['폐업일자'].dt.year)==int(year)) & (df_cal['업태구분명'].str.contains(subject))]
    print(df_calc.head())
    return len(df_calc)

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



@app.get(path='/getApiMongo')
async def getApiMongo():
    col = db['today_failed']
    data = col.find({},{"_id":0})
    
    if len(list(data)) == 0:
        data = await insertApiMongo()
    data_uptae = data['result']['body']['rows']['row']
    columns = data['result']['header']['columns']
    column_dict = {'교육/도서/완구/오락':0, '가전':0, '컴퓨터/사무용품':0, '가구/수납용품':0, '건강/식품':0, '의류/패션/잡화/뷰티':0, '자동차/자동차용품':0, '레져/여행/공연':0, '기타':0}
    today_failed = [item['uptaeNm'] for item in data_uptae]
    for i in column_dict:
        for j in today_failed:
            if i in j:
                column_dict[i] += 1
    # for i in range( )
    print(column_dict)
    return today_failed, column_dict

    # df = pd.DataFrame(list(json_string))
    # print(df.columns)
    # df_cal = df.iloc[:,[1,8]]
    # df_calc = df_cal.loc[((df_cal['폐업일자'].dt.year)==int(year)) & (df_cal['업태구분명'].str.contains(subject))]
    # print(df_calc.head())
    # return len(df_calc)

#mongo data delete
@app.get(path='/datasetDelete')
async def deleteData():
    col.delete_many({})
    return "deleted"

