import yfinance as yf
import pandas as pd

# 금(GC=F), 은(SI=F) 선물 시세 다운로드 (최근 1년)
gold = yf.download("GC=F", period="1y", interval="1d")
silver = yf.download("SI=F", period="1y", interval="1d")

print("=== 금(GC=F) 데이터 ===")
print(f"데이터 개수: {len(gold)}개")
print(gold.tail())

print("\n=== 은(SI=F) 데이터 ===")
print(f"데이터 개수: {len(silver)}개")
print(silver.tail())