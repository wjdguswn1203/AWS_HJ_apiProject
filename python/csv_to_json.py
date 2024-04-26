#!/usr/bin/env python
import csv
import json

csv_file_path = 'shoppingmall_closed.csv'


# csv 파일 읽어오기
with open(csv_file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # 첫 줄 skip

    # 각 라인마다 딕셔너리 생성 후 리스트에 추가
    data = []
    for line in reader:
        # if len(data) == 0:
        #     data.
        d = {
            'stateData': line[0],
            'closedDate': line[1],
            'address': line[2],
            'addressStreet': line[3],
            'postalAddress': line[4],
            'storeName': line[5],
            'lastDate': line[6],
            'renewal': line[7],
            'renewalDate': line[8],
            'subject': line[9],
            'addressX': line[10],
            'addressY': line[11]
        }
        data.append(d)

# json string으로 변환
data = {'shoppingmall_closed': data}
json_string = json.dumps(data, ensure_ascii=False, indent=2)


# txt 파일로 저장할 경로
txt_file_path = 'shoppingmall_closed_data.json'

# txt 파일 쓰기
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(json_string)