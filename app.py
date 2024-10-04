from flask import Flask, request, send_file
import io
import pandas as pd
import os
from datetime import datetime
import chardet
import requests
from io import StringIO


app = Flask(__name__)

def detect_encoding(file_content):
    result = chardet.detect(file_content)
    return result['encoding']
def download_csv_from_github(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        # 바이너리 데이터를 바로 반환
        return response.content
    else:
        print(f"Failed to download file: {file_url}")
        return None

@app.route('/AgriWeather', methods=['GET'])
def download_csv():
    # 파라미터 받아오기
    start_date = str(request.args.get('start_date'))  # ex. 20241004
    end_date = str(request.args.get('end_date'))  # ex. 20241004
    station_code = request.args.get('station_code')  # ex. 477802A001

    # 날짜를 datetime 객체로 변환
    start_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')

    df_list = []

    # GitHub에서 CSV 파일을 다운로드할 base URL
    base_url = 'https://raw.githubusercontent.com/danuni29/Agri-Weather-DB/refs/heads/master/Agri_Weather'

    # GitHub에서 station_code를 포함하는 폴더 찾기 (로컬 방식과 유사하게)
    response = requests.get(base_url)  # 전체 Agri_Weather 폴더 목록을 가져옴
    print(response)
    if response.status_code != 200:
        return "Failed to fetch the folder list from GitHub.", 500

    # 응답 데이터에서 폴더를 추출해야 하는데, 여기서는 HTML에서 station_code가 포함된 폴더를 찾음
    folders = response.text.splitlines()  # GitHub의 응답을 단순히 라인으로 나눔
    target_folder_name = None

    # station_code를 포함한 폴더를 찾는 로직
    for folder_name in folders:
        if station_code in folder_name:
            target_folder_name = folder_name
            break

    if target_folder_name is None:
        return "지역코드가 존재하지 않습니다.", 404

    target_folder_url = f"{base_url}/{target_folder_name}"

    # 시작 연도부터 끝 연도까지 반복하면서 필요한 데이터만 읽기
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month

        # 파일 경로 예시: Agri_Weather/가평군_가평읍_477802A001/2011/가평군_가평읍_477802A001_2011_05.csv
        file_name = f'{target_folder_name}_{year}_{month:02d}.csv'
        file_url = f"{target_folder_url}/{year}/{file_name}"
        print(f"Downloading {file_url}")

        # GitHub에서 파일 다운로드
        file_content = download_csv_from_github(file_url)

        # 파일이 존재하는지 확인
        if file_content:
            # 인코딩 감지 및 CSV 읽기
            encoding = detect_encoding(file_content)
            try:
                csv_data = io.BytesIO(file_content)  # BytesIO로 변환하여 처리
                month_df = pd.read_csv(csv_data, encoding=encoding)

                # 'no' 칼럼이 있으면 제거
                if 'no' in month_df.columns:
                    month_df = month_df.drop(columns=['no'])

                # 데이터가 있으면 리스트에 추가
                if not month_df.empty:
                    df_list.append(month_df)

            except Exception as e:
                print(f"Error reading {file_url}: {e}")
        else:
            print(f"No data found for {year}-{month:02d}")

        # 다음 달로 이동
        if month == 12:
            current_date = current_date.replace(year=year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=month + 1, day=1)

    # 모든 연도의 데이터를 하나의 데이터프레임으로 합치기
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        return "No data found for the specified period or station code.", 404

    # CSV 데이터를 바로 ByteIO에 저장하여 사용자에게 반환
    output = io.BytesIO()
    combined_df.to_csv(output, index=False, encoding='euc-kr')
    output.seek(0)

    return send_file(output,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'{station_code}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv')

if __name__ == '__main__':
    app.run(debug=True)