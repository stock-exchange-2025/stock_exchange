import os
import requests
from dotenv import load_dotenv

load_dotenv()

def handler(event, context):
    api_key = os.getenv("YC_MONITORING_API_KEY")
    folder_id = os.getenv("FOLDER_ID")
    monitoring_url = f"https://monitoring.api.cloud.yandex.net/monitoring/v2/data/write?folderId={folder_id}&service=custom"
    
    if not api_key or not folder_id:
        return {"statusCode": 500, "body": "Ошибка: YC_MONITORING_API_KEY или YC_FOLDER_ID не настроены"}
   
    metric = {
        "metrics": [{
            "name": "export_trades_completed",
            "labels": {
                "bucket": os.getenv("S3_BUCKET"),
                "environment": "production"
            },
            "value": 1
        }]
    }
    
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(monitoring_url, json=metric, headers=headers)
    
    if response.status_code == 200:
        return {"statusCode": 200, "body": "Метрика отправлена в Yandex Monitoring"}
    else:
        return {"statusCode": 500, "body": f"Ошибка Monitoring: {response.text}"}