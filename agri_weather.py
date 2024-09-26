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

        if not f'{spot}_{code}.csv' in os.listdir('output'):
            start_year = int(start_year.split('-')[0])
            print(f"코드{code} : {start_year}")
            #
            # except:
            #     start_year = 2000
            #     print(f"코드{code} : {start_year}")
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


                    if 'response' in xml_dict and 'body' in xml_dict['response']:
                        content = xml_dict['response']['body']['items']['item']

                        for i in range(len(content)):
                            new_df = pd.DataFrame(content[i], index=[0])
                            if new_df['temp'].values and new_df['hum'].values and new_df['rain'].values and new_df['wind'].values:
                                df = pd.concat([df, new_df])
                                df.to_csv(f'output/{spot}_{code}.csv', index=False, encoding='utf-8-sig')



    # print(response.status_code)
    #
    # df = pd.DataFrame()
    # print(response.json())
    # print(response.json()['data'])
    # df = pd.concat(df, pd.DataFrame(response.json()['data']))
    # print(df)

test()
# def main():
#
#     # 과거 기상 관측 데이터 가져오기
#     url = 'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V2/GnrlWeather/getWeatherYearDayList'
#     # serviceKey = 'CaNVjajLQjjwRIQMs8QNBr1uV86t3KkH5FT8sbOTcWIpZOyWUZ9VdEze/miJwopWCi4M4ayJAUAnXbTeogRGdA=='
#     serviceKey = 'cnFWOksdH2rQuZ9YQs2IR3frMjm2kgy8eauRY4ujdTSTvGEeDGXulTzCIJtU7htSZeFnoof4l6RGh3EpVIbo1Q%3D%3D'
#
#     params = {
#         'serviceKey': serviceKey,
#         'Page_No': 1,
#         'Page_Size': 100,
#         'search_Year': '2023',
#         'obsr_Spot_Code': '210913E001'
#     }
#
#     spot_df = pd.read_csv('obsr_spot_data.csv')
#     start_year = 1985
#     end_year = 1985
#
#
#     for code in spot_df['obsr_Spot_Code']:
#         print(f"코드{code}")
#         for year in range(start_year, end_year + 1):
#             params = {
#                 'serviceKey': serviceKey,
#                 'Page_No': 1,
#                 'Page_Size': 100,
#                 'search_Year': str(year),
#                 'obsr_Spot_Code': code
#             }
#     # try:
#     response = requests.get(url, params=params, verify=False)
#     # decoded_content = unquote(response.content.decode("utf-8"))
#     # print(decoded_content)
#     print(response.content)

# if __name__ == '__main__':
#     main()

# test()