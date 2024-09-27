import requests
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import pandas as pd
import xmltodict
import os


# 관측지점 데이터프레임 정리 (1회만 하면 됌)
def get_df():
    df = pd.read_csv('obsr_spot_data.csv', encoding='cp949')
    df.columns = df.iloc[0].values

    df = df[1:].reset_index(drop=True)
    df.to_csv('obsr_spot_data.csv', index=False, encoding='cp949')

def test():

    serviceKey = 'cnFWOksdH2rQuZ9YQs2IR3frMjm2kgy8eauRY4ujdTSTvGEeDGXulTzCIJtU7htSZeFnoof4l6RGh3EpVIbo1Q%3D%3D'
    #
    spot_df = pd.read_csv('obsr_spot_data.csv')
    end_year = 2023
    #
    for [code, start_year,spot] in spot_df[['지점코드', '관측시작일', '지점명']].values:
        print(f'{spot}_{code}.csv')
        if not f'{spot}_{code}.csv' in os.listdir('output'):
            print(f'{spot}_{code}.csv', start_year, '없음')
            try:
                start_year = int(start_year.split('-')[0])
            except:
                start_year = 2000

            # print(f"코드{code} : {start_year}")

            df = pd.DataFrame()

            for year in range(start_year, end_year + 1):
                params = {
                    'obsr_Spot_Code': code,
                    'search_Year': year,
                }
                for i in range(1,5):
                    url = f'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V2/GnrlWeather/getWeatherYearDayList?serviceKey=cnFWOksdH2rQuZ9YQs2IR3frMjm2kgy8eauRY4ujdTSTvGEeDGXulTzCIJtU7htSZeFnoof4l6RGh3EpVIbo1Q%3D%3D&Page_No={i}&Page_Size=100'

                    response = requests.get(url, params=params)

                    content = response.text
                    xml_dict = xmltodict.parse(content)
                    print(xml_dict)


                    if 'response' in xml_dict and 'body' in xml_dict['response']:
                        content = xml_dict['response']['body']['items']['item']
                        # print(f'response=={response.status_code} : {spot}_{code}.csv')
                        for i in range(len(content)):
                            new_df = pd.DataFrame(content[i], index=[0])
                            print(new_df)

                            if new_df['temp'].values or new_df['hum'].values:
                                df = pd.concat([df, new_df])
                                df.to_csv(f'output/{spot}_{code}.csv', index=False, encoding='utf-8-sig')
                                print(f'{spot}_{code}.csv 저장완료')
                            else:
                                print(f'{spot}_{code}.csv 누락데이터 ')

                    else:
                        print(f'{response.status_code} : {spot}_{code}.csv')

# 2000 ~ 2023년도 지점별로 받은 데이터 년도별 분류
def divide_df():
    path = 'output'
    for f in os.listdir(path):
        with open(f'{path}/{f}.csv', 'r', encoding='utf-8-sig') as file:
            df = pd.read_csv(f'{path}/{f}.csv')

            if not '2023-12-31' in df['date']:
                print(f)
                with open('누락데이터.csv', 'w') as file:
                    file.write(f"{f.split('_')[1]}")
            else:
                for year in range(2000, 2024):
                    df = df[df['date'] == year].split('-')[0]
                    df.to_csv(f'{path}/{f.split("_")[1]}_{year}.csv', index=False, encoding='utf-8-sig')

