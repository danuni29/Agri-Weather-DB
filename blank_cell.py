import pandas as pd
import os
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    # Provide a default encoding if detection fails
    if encoding is None:
        encoding = 'euc-kr'
    return encoding

# 지점 정보 CSV 파일 읽기
obsr_spot_info = pd.read_csv('obsr_spot_info.csv' ,encoding=detect_encoding('obsr_spot_info.csv'), skiprows=1, header=0)
# print(obsr_spot_info.columns)


# Agri_Weather 폴더 경로 설정
agri_weather_folder = 'Agri_Weather'

# Agri_Weather 폴더 내의 모든 폴더와 파일 순회
for root, dirs, files in os.walk(agri_weather_folder):
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(root, file)

            # CSV 파일 불러오기
            df = pd.read_csv(file_path, encoding=detect_encoding(file_path))

            # 지점코드(stn_Code)와 지점명(stn_Name)이 있는 경우에만 처리
            if 'stn_Code' in df.columns and 'stn_Name' in df.columns:
                # 지점명이 비어있는 경우에만 obsr_spot_info를 참조하여 채우기
                missing_spot_name = df['stn_Name'].isna()

                if missing_spot_name.any():
                    # 지점코드에 맞는 지점명을 obsr_spot_info에서 찾아서 채우기
                    df.loc[missing_spot_name, 'stn_Name'] = df.loc[missing_spot_name, 'stn_Code'].map(
                        obsr_spot_info.set_index('지점코드')['지점명'])

                    # 수정된 데이터를 다시 CSV로 저장
                    df.to_csv(file_path, index=False)
                    print(f'{file} 파일의 지점명이 obsr_spot_info를 참조하여 채워졌습니다.')