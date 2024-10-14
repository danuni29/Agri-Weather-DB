from flask import Flask, request, send_file
import io
import pandas as pd
from datetime import datetime
import chardet
import requests



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
    info_data = pd.read_csv('./obsr_spot_info.csv', encoding='euc-kr', header=1)

    # 파라미터 받아오기
    start_date = str(request.args.get('start_date'))  # ex. 20241004
    end_date = str(request.args.get('end_date'))  # ex. 20240914
    station_code = request.args.get('station_code')  # ex. 477802A001

    # 날짜를 datetime 객체로 변환
    start_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')

    df_list = []

    # GitHub에서 CSV 파일을 다운로드할 base URL
    base_url = 'https://raw.githubusercontent.com/danuni29/Agri-Weather-DB/master/Agri_Weather'

    region = info_data[info_data['지점코드'] == station_code]['지점명'].values[0]
    region = region.replace(" ", "_")

    target_folder_name = f"{region}_{station_code}"
    target_folder_url = f"{base_url}/{target_folder_name}"

    # 시작 연도부터 끝 연도까지 반복하면서 필요한 데이터만 읽기
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month

        # 파일 경로 예시: Agri_Weather/가평군_가평읍_477802A001/2024/가평군_가평읍_477802A001_2024_09.csv
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

                # 날짜 컬럼이 있는지 확인 (여기서는 'date'로 가정)
                if 'date' in month_df.columns:
                    # print(month_df)
                    month_df['date'] = pd.to_datetime(month_df['date'], format='%Y-%m-%d')

                    # 마지막 달인 경우 end_date를 기준으로 필터링
                    if year == end_date.year and month == end_date.month:
                        month_df = month_df[month_df['date'] <= end_date]

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