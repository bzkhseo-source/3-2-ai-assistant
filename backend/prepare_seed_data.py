import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def fetch_and_convert(ticker: str, label: str, period: str = "1y") -> list[dict]:
    """yfinance 데이터를 (date, value, memo) 레코드 리스트로 변환"""
    df = yf.download(ticker, period=period, interval="1d")
    # 멀티인덱스 컬럼 정리 (yfinance 최신 버전 대응)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    records = []
    for date, row in df.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(float(row["Close"]), 2),
            "memo": label
        })
    return records


def main():
    gold_records = fetch_and_convert("GC=F", "금", period="1y")
    silver_records = fetch_and_convert("SI=F", "은", period="1y")

    all_records = gold_records + silver_records
    all_records.sort(key=lambda r: (r["date"], r["memo"]))

    print(f"금 데이터: {len(gold_records)}개")
    print(f"은 데이터: {len(silver_records)}개")
    print(f"전체 합계: {len(all_records)}개")

    with open("seed_data.json", "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print("\nseed_data.json 저장 완료")
    print("샘플(앞 3개):")
    for r in all_records[:3]:
        print(r)


if __name__ == "__main__":
    main()