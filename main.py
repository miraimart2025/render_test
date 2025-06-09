import os
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import gspread
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

# 認証設定
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

json_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
if not json_path:
    raise FileNotFoundError("環境変数 'GOOGLE_SERVICE_ACCOUNT_JSON' が設定されていません。")

creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("問い合わせ一覧")
sheet = spreadsheet.sheet1

@app.post("/contact")
def receive_contact(form: ContactForm):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([form.name, form.email, form.message, now])
    return {"message": "スプレッドシートに保存しました！"}
