from flask import Flask, request, send_file
import io
import pandas as pd
import os
from datetime import datetime
import chardet


app = Flask(__name__)

@app.route('/AgriWeather', methods=['GET'])
def download_csv():
    # 파라미터 받아오기
    start_date = str(request.args.get('start_date')) # ex.20241004
    end_date = str(request.args.get('end_date')) # ex.20241004
    station_code = request.args.get('station_code') # ex.477802A001


    # 날짜를 datetime 객체로 변환
    start_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')

    df_list = []

    # Agri_Weather 폴더에서 station_code를 포함하는 폴더를 찾기
    base_path = './Agri_Weather'
    target_folder = None
    target_folder_name = None

    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path) and station_code in folder_name:
            target_folder = folder_path
            target_folder_name = folder_name

            break
    # print(target_folder)

    if target_folder is None:
        return "지역코드가 존재하지 않습니다.", 404

    # 시작 연도부터 끝 연도까지 반복하면서 필요한 데이터만 읽기
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month

        # 파일 경로 예시: Agri_Weather/가평군_가평읍_477802A001/2011/가평군_가평읍_477802A001_2011_05.csv
        folder_path = f'{target_folder}/{year}'
        file_name = f'{target_folder_name}_{year}_{month:02d}.csv'
        file_path = os.path.join(folder_path, file_name)
        print(file_name)

        # 파일이 존재하는지 확인
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding']

            try:
                # CSV 파일 읽기
                month_df = pd.read_csv(file_path, encoding=encoding)
                month_df = month_df.drop(columns=['no'])

            # 데이터가 있으면 리스트에 추가
                if not month_df.empty:
                    df_list.append(month_df)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
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


    output = io.BytesIO()
    combined_df.to_csv(output, index=False, encoding='euc-kr')
    output.seek(0)

    return send_file(output,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=f'{station_code}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv')



# http://localhost:5000/download?start_date=<START_DATE>&end_date=<END_DATE>&station_code=<STATION_CODE>
# AgriWeather?start_date=20231004&end_date=20240929&station_code=477802A001

if __name__ == '__main__':
    app.run(debug=True)