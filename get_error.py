import os
import pandas as pd

path = 'output'
dir_list = os.listdir(path)
f = dir_list[1]
print(f)
# for f in os.listdir(path):
with open(f'{path}/{f}', 'r', encoding='utf-8-sig') as file:
    df = pd.read_csv(f'{path}/{f}')

    df = df.drop(columns='no')
    # df = df['temp'] 가 없으면 pass

    for i in range(len(df)):
        if df['temp'][i] == '':
            pass
        else:
            df['temp'][i] = float(df['temp'][i])
            df['temp'][i] = round(df['temp'][i], 1)
            df['temp'][i] = str(df['temp'][i])



    print(df)