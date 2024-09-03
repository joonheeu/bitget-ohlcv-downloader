# Bitget OHLCV 데이터 다운로드 및 병합 도구

이 프로젝트는 Bitget 거래소의 특정 티커에 대한 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 다운로드하고, 다운로드한 파일을 병합하여 Excel 및 CSV 형식으로 저장하는 Python 기반의 도구입니다.

## 주요 기능

- **OHLCV 데이터 다운로드**: Bitget에서 특정 티커에 대한 과거 1분봉 OHLCV 데이터를 다운로드합니다.
- **데이터 추출 및 병합**: 다운로드한 zip 파일에서 데이터를 추출하고 병합합니다.
- **사용자 정의 기간 지원**: 지정된 날짜 범위의 데이터를 다운로드할 수 있습니다.
- **컬럼명 자동 변경**: 컬럼명을 `datetime`, `open`, `high`, `low`, `close`, `volume`, `quote_volume`으로 자동 변경합니다.
- **Excel 및 CSV 파일 저장**: 병합된 데이터를 Excel 파일로 저장한 후, CSV 파일로도 변환하여 저장합니다.
- **에러 처리 및 로깅**: 다운로드 실패 시 에러를 로그로 기록하고, 연속된 실패 횟수에 따라 실행을 중단합니다.
- **진행 상황 추적**: `tqdm`을 사용해 다운로드 진행 상황과 남은 시간을 표시합니다.

## 요구 사항

- Python 3.7 이상
- `pandas`
- `requests`
- `tqdm`
- `openpyxl`

## 설치

필수 패키지를 설치하려면 다음 명령어를 실행하세요:

```bash
pip install pandas requests tqdm openpyxl
```

## 사용 방법

1. **레포지토리 클론**

    ```bash
    git clone https://github.com/joonheeu/bitget-ohlcv-downloader.git
    cd bitget-ohlcv-downloader
    ```

2. **스크립트 실행**

    스크립트를 직접 실행하여 데이터를 다운로드하고, 병합한 뒤 Excel 및 CSV 파일로 저장할 수 있습니다.

    ```bash
    python main.py
    ```

3. **파라미터 사용자 정의**

    `main.py` 파일 내의 `if __name__ == '__main__'` 블록에서 다음 파라미터를 사용자 정의할 수 있습니다:

    - **`ticker`**: 다운로드할 암호화폐 페어 (예: `BTCUSDT`).
    - **`from_date`**: 데이터 다운로드 시작 날짜 (형식: `YYYYMMDD`).
    - **`to_date`**: (선택 사항) 데이터 다운로드 종료 날짜. 지정하지 않으면 현재 날짜까지 다운로드합니다.
    - **`interval_seconds`**: 각 다운로드 시도 사이의 간격 (초 단위).
    - **`max_retries`**: 연속된 실패 시도 횟수. 이 횟수 이상 실패하면 다운로드가 중단됩니다.
    - **`convert_timestamp`**: `timestamp`를 사람이 읽을 수 있는 `datetime` 형식으로 변환할지 여부 (True/False).

4. **결과 확인**

    다운로드 및 병합된 데이터는 `downloads/<ticker>` 폴더에 저장됩니다:

    - 병합된 Excel 파일: `<ticker>_merged.xlsx`
    - 병합된 CSV 파일: `<ticker>_merged.csv`

    에러 발생 시, 해당 폴더 내에 `error.log` 파일에 에러가 기록됩니다.

## 사용 예시

다음은 `BTCUSDT` 데이터를 2019년 7월 10일부터 현재까지 다운로드하고 병합하는 예시입니다:

```python
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
```

이 예시에서:

- `BTCUSDT` 티커 데이터를 `2019년 7월 10일`부터 현재까지 다운로드합니다.
- 다운로드된 데이터를 병합하여 Excel 파일 (`BTCUSDT_merged.xlsx`)로 저장하고, 이를 CSV 파일 (`BTCUSDT_merged.csv`)로 변환합니다.

## 에러 처리

- 특정 날짜의 데이터를 다운로드하거나 추출하는 데 실패하면 최대 10회(기본값)까지 재시도하며, 실패가 연속되면 실행이 중단됩니다.
- 발생한 에러는 `error.log` 파일에 기록됩니다.

## 기여

이 프로젝트에 기여하고 싶다면 레포지토리를 포크하고, 수정 사항을 반영한 후 풀 리퀘스트를 제출하세요. 모든 기여 및 제안을 환영합니다!

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.