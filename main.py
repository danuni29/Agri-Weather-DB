
import requests
import pandas as pd



spot_df = pd.read_csv('spot_nm.csv')

start_year = 2000
end_year = 2023

for code in spot_df['지점코드']:
    print(f"코드{code}")
    for year in range(start_year, end_year + 1):
        params = {
            'serviceKey': serviceKey,
            'Page_No': 1,
            'Page_Size': 100,
            'search_Year': str(year),
            'obsr_Spot_Code': code
        }
# try:
response = requests.get(url, params=params)
decoded_content = unquote(response.content.decode("utf-8"))
print(decoded_content)