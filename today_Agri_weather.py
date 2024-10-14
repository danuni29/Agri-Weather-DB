import os
from datetime import datetime, timedelta
import requests
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import pandas as pd


def main():
    now = datetime.now()
    now_date = now.date() - timedelta(days=1)
    now_year = now.year
    now_month = now.month
    print(now_date)


    info_df = pd.read_csv('obsr_spot_info.csv', encoding='euc-kr', header=1)
    data_list = []

    for code, region in zip(info_df['지점코드'], info_df['지점명']):
        serviceKey = 'cnFWOksdH2rQuZ9YQs2IR3frMjm2kgy8eauRY4ujdTSTvGEeDGXulTzCIJtU7htSZeFnoof4l6RGh3EpVIbo1Q%3D%3D'

        url = f'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V2/GnrlWeather/getWeatherTermDayList?serviceKey={serviceKey}'
        params = {
            'Page_No': 1,
            'Page_Size': 10,
            'begin_Date': '2024-10-11',
            'end_Date': '2024-10-13',
            'obsr_Spot_Code': code,
        }

        response = requests.get(url, params=params)
        decoded_content = unquote(response.content.decode("utf-8"))
        print(response.status_code)
        print(decoded_content)
        # XML 파싱
        root = ET.fromstring(decoded_content)
        for item in root.findall('.//item'):
            data = {
                'stn_Code': item.find('stn_Code').text,
                'stn_Name': item.find('stn_Name').text,
                'date': item.find('date').text,
                'temp': item.find('temp').text,
                'max_Temp': item.find('max_Temp').text,
                'min_Temp': item.find('min_Temp').text,
                'hum': item.find('hum').text,
                'widdir': item.find('widdir').text,
                'wind': item.find('wind').text,
                'max_Wind': item.find('max_Wind').text,
                'rain': item.find('rain').text,
                'sun_Time': item.find('sun_Time').text,
                'sun_Qy': item.find('sun_Qy').text,
                'condens_Time': item.find('condens_Time').text,
                'gr_Temp': item.find('gr_Temp').text,
                'soil_Temp': item.find('soil_Temp').text,
                'soil_Wt': item.find('soil_Wt').text
            }
            data_list.append(data)

    df = pd.DataFrame(data_list)
    print(df)

    # 각 관측소 코드에 해당하는 폴더에 데이터를 저장합니다
    for code in df['stn_Code'].unique():
        # 해당 코드 데이터만 추출
        station_df = df[df['stn_Code'] == code]

        # 폴더명 생성 (예: 가평군_가평읍_477802A001)
        folder_name = f"{station_df['stn_Name'].iloc[0].replace(' ', '_')}_{code}"
        folder_path = os.path.join('./Agri_Weather', folder_name, str(now_year))

        # 연도 및 월별 파일 이름 생성
        file_name = f"{station_df['stn_Name'].iloc[0].replace(' ', '_')}_{code}_{now_year}_{now_month}.csv"
        full_path = os.path.join(folder_path, file_name)

        ## 파일이 존재하면 데이터를 append, 존재하지 않으면 생성
        if os.path.exists(full_path):
            # 파일이 존재할 때 기존 데이터를 불러옴
            existing_df = pd.read_csv(full_path, encoding='euc-kr')

            # 기존 데이터와 새로운 데이터 결합
            combined_df = pd.concat([existing_df, station_df], ignore_index=True)

            # 중복된 행 제거
            combined_df = combined_df.drop_duplicates(subset=['date'], keep='first')
            print(f'중복 행 제거 후 데이터 결합 완료: {full_path}')
            print(combined_df)
        else:
            combined_df = station_df

        # 데이터 저장
        combined_df.to_csv(full_path, index=False, encoding='euc-kr')
        # print(f"Data saved to {full_path}")

if __name__ == '__main__':
    main()
