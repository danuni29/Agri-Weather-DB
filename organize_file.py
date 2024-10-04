import os
import pandas as pd
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    # Provide a default encoding if detection fails
    if encoding is None:
        encoding = 'euc-kr'
    return encoding

def main():
    base_dir = './Agri_Weather'


    for region_folder in os.listdir(base_dir):
        region_path = os.path.join(base_dir, region_folder)

        # Skip if it's not a directory
        if not os.path.isdir(region_path):
            continue


        for csv_file in os.listdir(region_path):
            if csv_file.endswith(".csv"):
                original_path = os.path.join(region_path, csv_file)

                df = pd.read_csv(original_path, encoding=detect_encoding(original_path))


                df['date'] = pd.to_datetime(df['date'], errors='coerce')

                # Drop rows with invalid dates
                df = df.dropna(subset=['date'])

                # Extract year and month from the date column
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                df['day'] = df['date'].dt.day

                # Group data by year and month
                grouped = df.groupby(['year', 'month'])

                for (year, month), group in grouped:
                    # Define the folder path based on the year
                    year_folder = os.path.join(region_path, str(year))
                    os.makedirs(year_folder, exist_ok=True)

                    # Define the filename based on the year and month
                    monthly_filename = f"{region_folder}_{year}_{month:02d}.csv"
                    monthly_path = os.path.join(year_folder, monthly_filename)

                    # Save the group data to the CSV file
                    group.to_csv(monthly_path, index=False, encoding=detect_encoding(original_path))
                    print(f"저장완료!: {monthly_path}")

                os.remove(original_path)
                print(f"삭제완료!: {original_path}")


if __name__ == '__main__':
    main()