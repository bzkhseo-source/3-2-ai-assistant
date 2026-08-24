import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def get_firestore_client():
    """Firestore 클라이언트를 싱글톤으로 반환 (앱 전체에서 하나만 초기화)"""
    global _db
    if _db is not None:
        return _db

    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON 환경변수가 설정되지 않았습니다. "
            ".env 파일을 확인해주세요."
        )

    try:
        service_account_info = json.loads(service_account_json)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"FIREBASE_SERVICE_ACCOUNT_JSON 파싱 실패: {e}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db