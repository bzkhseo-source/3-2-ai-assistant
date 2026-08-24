import json
from dotenv import load_dotenv

load_dotenv()

from app.services.firestore_service import get_firestore_client

COLLECTION_NAME = "data"
BATCH_SIZE = 400  # Firestore 배치 쓰기 한도(500) 이내로 여유있게 설정


def main():
    with open("seed_data.json", "r", encoding="utf-8") as f:
        records = json.load(f)

    db = get_firestore_client()

    # 기존 데이터 삭제 여부 확인 (중복 업로드 방지)
    existing = list(db.collection(COLLECTION_NAME).limit(1).stream())
    if existing:
        answer = input(
            f"'{COLLECTION_NAME}' 컬렉션에 이미 데이터가 있습니다. "
            "계속 진행하면 중복 데이터가 쌓일 수 있습니다. 계속할까요? (y/n): "
        )
        if answer.lower() != "y":
            print("취소되었습니다.")
            return

    total = len(records)
    uploaded = 0

    for i in range(0, total, BATCH_SIZE):
        chunk = records[i:i + BATCH_SIZE]
        batch = db.batch()
        for record in chunk:
            doc_ref = db.collection(COLLECTION_NAME).document()
            batch.set(doc_ref, record)
        batch.commit()
        uploaded += len(chunk)
        print(f"진행: {uploaded}/{total}")

    print(f"\n업로드 완료: 총 {uploaded}개")


if __name__ == "__main__":
    main()