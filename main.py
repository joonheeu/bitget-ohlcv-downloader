import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import zipfile
from tqdm import tqdm

class BitgetDataDownloader:
    def __init__(self, ticker, base_download_folder='./downloads', interval_seconds=1, max_retries=10):
        self.ticker = ticker
        self.base_download_folder = base_download_folder
        self.interval_seconds = interval_seconds
        self.max_retries = max_retries
        self.download_folder = os.path.join(self.base_download_folder, self.ticker)
        self.ensure_directory_exists(self.download_folder)

    def ensure_directory_exists(self, path):
        """디렉토리가 존재하지 않으면 생성합니다."""
        if not os.path.exists(path):
            os.makedirs(path)

    def format_date(self, date_str):
        """YYYYMMDD 형식의 문자열을 datetime 객체로 변환합니다."""
        return datetime.strptime(date_str, '%Y%m%d')

    def build_url(self, date_str):
        """다운로드할 ZIP 파일의 URL을 생성합니다."""
        return f"https://img.bitgetimg.com/online/kline/{self.ticker}/{self.ticker}_UMCBL_1min_{date_str}.zip"

    def download_file(self, url, download_path):
        """URL에서 파일을 다운로드하여 지정된 경로에 저장합니다."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # 요청이 성공했는지 확인
            with open(download_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {download_path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Download failed for {url}: {e}")
            return False

    def extract_zip_file(self, zip_file_path, extract_to):
        """ZIP 파일을 지정된 경로에 압축 해제합니다."""
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"Extracted: {zip_file_path}")
            return True
        except zipfile.BadZipFile:
            print(f"Failed to extract {zip_file_path}: Bad ZIP file")
            return False

    def remove_file(self, file_path):
        """지정된 파일을 삭제합니다."""
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")

    def log_error(self, message):
        """에러 메시지를 로그 파일에 기록합니다."""
        log_file = os.path.join(self.download_folder, "error.log")
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def download_and_extract_chart_data(self, from_date, to_date=None):
        """지정된 날짜 범위 내의 모든 데이터를 다운로드하고 압축 해제합니다."""
        if to_date is None:
            to_date = datetime.now().strftime('%Y%m%d')

        from_date = self.format_date(from_date)
        to_date = self.format_date(to_date)
        
        current_date = from_date
        retries = 0

        # tqdm을 사용해 반복문의 진행률과 남은 시간을 표시합니다.
        date_range = (to_date - from_date).days + 1
        for _ in tqdm(range(date_range), desc=f"Downloading {self.ticker} data"):
            date_str = current_date.strftime('%Y%m%d')
            url = self.build_url(date_str)
            zip_file_path = os.path.join(self.download_folder, f"{self.ticker}_{date_str}.zip")
            
            if self.download_file(url, zip_file_path):
                if self.extract_zip_file(zip_file_path, self.download_folder):
                    self.remove_file(zip_file_path)
                    retries = 0  # 성공하면 실패 횟수 초기화
            else:
                retries += 1
                self.log_error(f"Failed to download or extract data for {date_str}")
                if retries >= self.max_retries:
                    self.log_error(f"Aborting after {retries} consecutive failures")
                    print(f"Aborting after {retries} consecutive failures")
                    break

            current_date += timedelta(days=1)
            time.sleep(self.interval_seconds)

class ExcelMerger:
    def __init__(self, ticker_folder, output_file, save_as='csv', convert_timestamp=False):
        self.ticker_folder = ticker_folder
        self.output_file = output_file
        self.save_as = save_as.lower()  # 'csv' 또는 'excel'
        self.convert_timestamp = convert_timestamp

    def convert_timestamp_to_datetime(self, df):
        """DataFrame의 timestamp를 YYYY/MM/DD HH:MM:SS 형식으로 변환합니다."""
        df['datetime'] = pd.to_datetime(df['datetime'], unit='s').dt.strftime('%Y/%m/%d %H:%M:%S')
        return df

    def remove_duplicate_columns(self, df):
        """DataFrame에서 중복된 컬럼명을 제거합니다."""
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def merge_excel_files(self):
        """지정된 티커 폴더 내의 모든 엑셀 파일을 하나로 통합하여 CSV 또는 Excel 파일로 저장합니다."""
        excel_files = [f for f in os.listdir(self.ticker_folder) if f.endswith('.xlsx')]
        dataframes = []

        for file in excel_files:
            file_path = os.path.join(self.ticker_folder, file)
            print(f"Reading {file_path}...")
            df = pd.read_excel(file_path)

            # 컬럼명을 변경합니다.
            df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']

            # 중복 컬럼 제거
            df = self.remove_duplicate_columns(df)

            dataframes.append(df)

        merged_df = pd.concat(dataframes, ignore_index=True)

        # 중복 컬럼 최종 제거 (다시 한 번 확인)
        merged_df = self.remove_duplicate_columns(merged_df)

        # 시간 순서대로 정렬
        merged_df['datetime'] = pd.to_datetime(merged_df['datetime'], unit='s')
        merged_df = merged_df.sort_values(by='datetime').reset_index(drop=True)

        # timestamp를 사람이 읽을 수 있는 형식으로 변환
        if self.convert_timestamp:
            merged_df = self.convert_timestamp_to_datetime(merged_df)

        # 데이터 저장 (CSV 또는 Excel)
        if self.save_as == 'excel':
            merged_df.to_excel(self.output_file, index=False)
            print(f"Saved merged data to Excel file: {self.output_file}")
        else:
            merged_df.to_csv(self.output_file, index=False)
            print(f"Saved merged data to CSV file: {self.output_file}")


if __name__ == '__main__':
    # BTCUSDT 데이터를 2019년 7월 10일부터 현재까지 다운로드하고 압축 해제합니다.
    downloader = BitgetDataDownloader("BTCUSDT", interval_seconds=1, max_retries=10)
    downloader.download_and_extract_chart_data("20190710")
    
    # 다운로드된 데이터를 병합하여 하나의 Excel 파일로 저장한 뒤, 이를 다시 CSV 파일로 저장합니다.
    ticker_folder = './downloads/BTCUSDT'  # 다운로드된 데이터가 저장된 폴더
    output_excel = './downloads/BTCUSDT_merged.xlsx'  # 결과를 저장할 Excel 파일 경로
    output_csv = './downloads/BTCUSDT_merged.csv'  # 결과를 저장할 CSV 파일 경로
    merger = ExcelMerger(ticker_folder, output_excel, output_csv, convert_timestamp=True)
    merger.merge_excel_files()

    # 자세한 주석:
    # - BitgetDataDownloader 클래스는 OHLCV 데이터를 다운로드하고 ZIP 파일을 압축 해제하는 작업을 수행합니다.
    # - 다운로드 시 진행 상황과 남은 시간을 tqdm 라이브러리를 통해 표시합니다.
    # - 10회 연속 다운로드 실패 시 작업을 중단하고, 에러 로그를 다운로드 폴더 내 error.log 파일에 기록합니다.
    # - ExcelMerger 클래스는 다운로드된 엑셀 파일들을 병합하여 하나의 Excel 파일로 저장한 후, 이를 다시 CSV 파일로 저장합니다.
    # - 컬럼명을 datetime, open, high, low, close, volume, quote_volume으로 변경하며, timestamp는 사람이 읽을 수 있는 형식으로 변환할 수 있습니다.
    # - `if __name__ == '__main__'` 아래에 제공된 예제는 BTCUSDT 티커 데이터를 2019년 7월 10일부터 현재까지 다운로드하고, 모든 데이터를 병합하여 Excel 파일과 CSV 파일로 저장하는 전체 프로세스를 보여줍니다.
