import json
from app.services.data_service import calculate_summary

with open("seed_data.json", "r", encoding="utf-8") as f:
    records = json.load(f)

summary = calculate_summary(records)
print(json.dumps(summary, ensure_ascii=False, indent=2))