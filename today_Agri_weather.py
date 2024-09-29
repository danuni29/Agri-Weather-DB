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

    # 관측소 정보를 읽어옵니다
    info_df = pd.read_csv('obsr_spot_info.csv', encoding='euc-kr', header=1)
    data_list = []

    # 각 관측소 코드에 대해 데이터를 가져옵니다
    for code, region in zip(info_df['지점코드'], info_df['지점명']):
        serviceKey = 'cnFWOksdH2rQuZ9YQs2IR3frMjm2kgy8eauRY4ujdTSTvGEeDGXulTzCIJtU7htSZeFnoof4l6RGh3EpVIbo1Q%3D%3D'

        url = f'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V2/GnrlWeather/getWeatherTermDayList?serviceKey={serviceKey}'
        params = {
            'Page_No': 1,
            'Page_Size': 100,
            'begin_Date': now_date,
            'end_Date': now_date,
            'obsr_Spot_Code': code,
        }

        response = requests.get(url, params=params)
        decoded_content = unquote(response.content.decode("utf-8"))

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

    # 각 관측소 코드에 해당하는 폴더에 데이터를 저장합니다
    for code in df['stn_Code'].unique():
        # 해당 코드 데이터만 추출
        station_df = df[df['stn_Code'] == code]

        # 폴더명 생성 (예: 가평군_가평읍_477802A001)
        folder_name = f"{station_df['stn_Name'].iloc[0].replace(' ', '_')}_{code}"
        folder_path = os.path.join('./Agri_Weather', folder_name)

        # 폴더가 존재하지 않으면 생성
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 연도별 파일 이름 생성
        file_name = f"{station_df['stn_Name'].iloc[0].replace(' ', '_')}_{code}_{now_year}.csv"
        full_path = os.path.join(folder_path, file_name)

        # 파일이 존재하면 데이터를 append, 존재하지 않으면 생성
        if os.path.exists(full_path):
            existing_df = pd.read_csv(full_path, encoding='euc-kr')
            if existing_df.iloc[-1, 2] == now_date:
                print('데이터가 중복되었습니다.')

            else:
                combined_df = pd.concat([existing_df, station_df], ignore_index=True)
        else:
            combined_df = station_df

        # 데이터 저장
        combined_df.to_csv(full_path, index=False, encoding='euc-kr')
        # print(f"Data saved to {full_path}")

def get_droped_data():
    now = datetime.now()
    now_year = now.year

    df = pd.read_csv(f'Agri_Weather/가평군_가평읍_477802A001/가평군_가평읍_477802A001_{now_year}.csv', encoding='euc-kr', header=1)

    print(df)
    if df.iloc[-2, 2] == now.date() - timedelta(days=2):
        print('데이터가 드랍되지 않았습니다.')

    else:
        print(f'{df.iloc[-2, 2]}  ===> {now.date() - timedelta(days=2)}')
        print('데이터가 드랍되었습니다.')
        last_date = df.iloc[-2, 2]
        last_date = datetime.strptime(last_date, '%Y-%m-%d').date()

        print('마지막 데이터:', last_date)
        droped_count = (now.date() - last_date).days
        # print('드랍된 날짜 수:', droped_count.days)
        droped_date = [ now.date() - timedelta(days=i) for i in range(1, droped_count)]
        print(droped_date)
        droped_date.sort()

        print('드랍된 날짜:', droped_date)

        for date in droped_date:
            # 관측소 정보를 읽어옵니다
            info_df = pd.read_csv('obsr_spot_info.csv', encoding='euc-kr', header=1)
            data_list = []

            # 각 관측소 코드에 대해 데이터를 가져옵니다
            for code, region in zip(info_df['지점코드'], info_df['지점명']):
                serviceKey = 'cnFWOksdH2rQuZ9YQs2IR3frMjm2kgy8eauRY4ujdTSTvGEeDGXulTzCIJtU7htSZeFnoof4l6RGh3EpVIbo1Q%3D%3D'

                url = f'http://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V2/GnrlWeather/getWeatherTermDayList?serviceKey={serviceKey}'
                params = {
                    'Page_No': 1,
                    'Page_Size': 100,
                    'begin_Date': date,
                    'end_Date': date,
                    'obsr_Spot_Code': code,
                }

                response = requests.get(url, params=params)
                decoded_content = unquote(response.content.decode("utf-8"))

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

            # 각 관측소 코드에 해당하는 폴더에 데이터를 저장합니다
            for code in df['stn_Code'].unique():
                # 해당 코드 데이터만 추출
                station_df = df[df['stn_Code'] == code]

                # 폴더명 생성 (예: 가평군_가평읍_477802A001)
                folder_name = f"{station_df['stn_Name'].iloc[0].replace(' ', '_')}_{code}"
                folder_path = os.path.join('./Agri_Weather', folder_name)

                # 폴더가 존재하지 않으면 생성
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # 연도별 파일 이름 생성
                file_name = f"{station_df['stn_Name'].iloc[0].replace(' ', '_')}_{code}_{now_year}.csv"
                full_path = os.path.join(folder_path, file_name)

                # 파일이 존재하면 데이터를 append, 존재하지 않으면 생성
                if os.path.exists(full_path):
                    # 파일이 존재하더라고 빈 날짜 체크하여 자동으로 추가
                    existing_df = pd.read_csv(full_path, encoding='euc-kr')
                    existing_df = existing_df.drop(df.index[-1])
                    print(existing_df)

                    print(f'마지막 행 드랍: {full_path}')
                    combined_df = pd.concat([existing_df, station_df], ignore_index=True)
                    print(f'빈 데이터 결합 완.: {full_path}')
                    print(combined_df)
                else:
                    combined_df = station_df

                # 데이터 저장
                combined_df.to_csv(full_path, index=False, encoding='euc-kr')
                # print(f"Data saved to {full_path}")

# get_droped_data()

if __name__ == '__main__':
    main()