import os
import json
import tempfile
import gspread
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

# 環境変数からサービスアカウントのJSON文字列を取得
json_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if not json_str:
    raise ValueError("環境変数 'GOOGLE_SERVICE_ACCOUNT_JSON' が設定されていません。")

# 一時ファイルに書き込む
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as temp_file:
    temp_file.write(json_str)
    temp_file_path = temp_file.name

# 認証とシート操作
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(temp_file_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("問い合わせ一覧")
sheet = spreadsheet.sheet1

@app.post("/contact")
def receive_contact(form: ContactForm):
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([form.name, form.email, form.message, now])
    return {"message": "スプレッドシートに保存しました！"}
