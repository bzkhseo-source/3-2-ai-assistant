from fastapi import APIRouter, HTTPException
from app.models.data import DataCreate, DataUpdate, DataResponse
from app.services.firestore_service import get_firestore_client
from app.services.data_service import calculate_summary
from app.services.data_service import calculate_summary, calculate_statistics
import yfinance as yf
from datetime import datetime
router = APIRouter(prefix="/api/data", tags=["data"])

COLLECTION_NAME = "data"


@router.post("", response_model=DataResponse)
def create_data(item: DataCreate):
    """새 데이터 추가"""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document()
    doc_ref.set(item.model_dump())
    return DataResponse(id=doc_ref.id, **item.model_dump())


@router.get("", response_model=list[DataResponse])
def list_data():
    """데이터 목록 조회"""
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append(DataResponse(id=doc.id, **data))
    return result


@router.put("/{item_id}", response_model=DataResponse)
def update_data(item_id: str, item: DataUpdate):
    """데이터 수정"""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(item_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"데이터를 찾을 수 없습니다: {item_id}")

    update_data_dict = {k: v for k, v in item.model_dump().items() if v is not None}
    if not update_data_dict:
        raise HTTPException(status_code=400, detail="수정할 값이 없습니다.")

    doc_ref.update(update_data_dict)
    updated_doc = doc_ref.get().to_dict()
    return DataResponse(id=item_id, **updated_doc)


@router.delete("/{item_id}")
def delete_data(item_id: str):
    """데이터 삭제"""
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(item_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"데이터를 찾을 수 없습니다: {item_id}")

    doc_ref.delete()
    return {"message": "삭제되었습니다.", "id": item_id}


@router.get("/summary")
def get_summary():
    """데이터 요약 (AI 프롬프트 주입용)"""
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()
    records = [doc.to_dict() for doc in docs]
    return calculate_summary(records)

@router.get("/statistics")
def get_statistics():
    """추가 통계 지표 (보너스: 변동성, 최근 7일 변화율)"""
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).stream()
    records = [doc.to_dict() for doc in docs]
    return calculate_statistics(records)

@router.post("/sync-latest")
def sync_latest_prices():
    """야후 파이낸스에서 금/은 최신 시세를 가져와 신규 데이터만 Firestore에 추가한다."""
    db = get_firestore_client()
    tickers = {"GC=F": "금", "SI=F": "은"}
    added = []
    skipped = []

    for ticker, label in tickers.items():
        try:
            df = yf.download(ticker, period="5d", interval="1d", progress=False)
            if isinstance(df.columns, __import__("pandas").MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty:
                skipped.append({"memo": label, "reason": "야후 파이낸스 데이터 없음"})
                continue

            latest_row = df.iloc[-1]
            latest_date = df.index[-1].strftime("%Y-%m-%d")
            latest_value = round(float(latest_row["Close"]), 2)

            # 같은 날짜 + 같은 구분(memo)이 이미 있는지 확인 (중복 방지)
            existing = list(
                db.collection(COLLECTION_NAME)
                .where("date", "==", latest_date)
                .where("memo", "==", label)
                .limit(1)
                .stream()
            )
            if existing:
                skipped.append({"memo": label, "date": latest_date, "reason": "이미 존재함"})
                continue

            doc_ref = db.collection(COLLECTION_NAME).document()
            doc_ref.set({"date": latest_date, "value": latest_value, "memo": label})
            added.append({"memo": label, "date": latest_date, "value": latest_value})

        except Exception as e:
            skipped.append({"memo": label, "reason": f"오류: {str(e)}"})

    return {"added": added, "skipped": skipped}