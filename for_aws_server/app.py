from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
import io
import pandas as pd
from datetime import datetime
import chardet
import requests
import os
from urllib.parse import quote

app = FastAPI()

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()
        result = chardet.detect(file_content)
    return result['encoding']

def download_csv_from_github(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        # 바이너리 데이터를 반환
        return response.content
    else:
        print(f"Failed to download file: {file_url}")
        return None


def generate_html_response(combined_df):
    # CSS 스타일 추가
    html_content = f"""
    <html>
    <head>
        <style>
            table {{
                width: 80%;
                margin: auto;
                border-collapse: collapse;
                text-align: center;
                font-family: Arial, sans-serif;
            }}
            th, td {{
                padding: 8px;
                border: 1px solid #ddd;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #ddd;
            }}
            caption {{
                caption-side: top;
                font-size: 1.5em;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <table>
            <caption>Data Table</caption>
            {combined_df.to_html(index=False, border=0)}
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)



@app.get("/")
def download_data(
    start_date: str,
    end_date: str,
    region: str,
    format: str = Query("csv", description="Desired output format: csv or html")  # 기본 형식은 csv
):
    base_folder = 'Agri_Weather'
    # obsr_spot_info.csv 파일을 읽어오기
    info_data = pd.read_csv('./region_info.csv', encoding='euc-kr')
    # print(info_data.columns)
    # 날짜를 datetime 객체로 변환
    start_date = datetime.strptime(start_date, '%Y%m%d')
    end_date = datetime.strptime(end_date, '%Y%m%d')

    df_list = []

    # 지점명 설정
    station_code_data = info_data[info_data['input_region'] == region]['지점코드']
    station_code = station_code_data.values[0]

    real_region_data = info_data[info_data['input_region'] == region]['지점명']
    real_region = real_region_data.values[0].replace(" ", "_")
    # region_formatted = region.replace(" ", "_")

    # 로컬 경로 설정
    target_folder_name = f"{real_region}_{station_code}"
    target_folder_path = os.path.join(base_folder, target_folder_name)
    print(target_folder_name)

    # 입력된 기간의 연도들을 계산하여 처리
    for year in range(start_date.year, end_date.year + 1):
        # 연도별 파일 경로 설정
        file_name = f'{target_folder_name}_{year}.csv'
        file_path = os.path.join(target_folder_path, file_name)
        print(f"Reading {file_path}")

        # 로컬 파일에서 데이터 읽기
        if os.path.exists(file_path):
            try:
                # CSV 파일 읽기
                year_df = pd.read_csv(file_path, encoding='utf-8-sig')

                # 'no' 칼럼이 있으면 제거
                if 'no' in year_df.columns:
                    year_df = year_df.drop(columns=['no'])

                # 날짜 컬럼이 있는지 확인 (여기서는 'date'로 가정)
                if 'date' in year_df.columns:
                    year_df['date'] = pd.to_datetime(year_df['date'], format='%Y-%m-%d')

                    # 시작 연도 또는 끝 연도의 경우 날짜 필터링
                    if year == start_date.year:
                        year_df = year_df[year_df['date'] >= start_date]
                    if year == end_date.year:
                        year_df = year_df[year_df['date'] <= end_date]

                    # 데이터가 있으면 리스트에 추가
                    if not year_df.empty:
                        df_list.append(year_df)

            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"No data found for {year}")

    # 모든 연도의 데이터를 하나의 데이터프레임으로 합치기
    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        raise HTTPException(status_code=404, detail="No data found for the specified period or station code.")

    # 사용자 요청에 따라 CSV 또는 HTML 형식으로 반환
    if format.lower() == "csv":
        # CSV 데이터를 ByteIO에 저장하여 반환
        output = io.BytesIO()
        combined_df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        output_filename = f"{region}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        encoded_filename = quote(output_filename)

        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        })

    elif format.lower() == "html":

        # HTML 형식으로 데이터를 반환

        html_content = f"""
        
            <html>
        
            <head>
        
                <style>
        
                    table {{
        
                        width: 80%;
        
                        margin: auto;
        
                        border-collapse: collapse;
        
                        text-align: center;
        
                        font-family: Arial, sans-serif;
        
                    }}
        
                    th, td {{
        
                        padding: 8px;
        
                        border: 1px solid #ddd;
        
                    }}
        
                    th {{
        
                        background-color: #4CAF50;
        
                        color: white;
        
                    }}
        
                    tr:nth-child(even) {{
        
                        background-color: #f2f2f2;
        
                    }}
        
                    tr:hover {{
        
                        background-color: #ddd;
        
                    }}
        
                    caption {{
        
                        caption-side: top;
        
                        font-size: 1.5em;
        
                        margin-bottom: 10px;
        
                    }}
        
                </style>
        
            </head>
        
            <body>
        
                <table>
        

        
                    {combined_df.to_html(index=False, border=0, escape=False)}
        
                </table>
        
            </body>
        
            </html>
        
            """

        return HTMLResponse(content=html_content)

    else:
        raise HTTPException(status_code=400, detail="Invalid format. Please choose 'csv' or 'html'.")

