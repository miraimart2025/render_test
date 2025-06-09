from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 実運用なら許可したいオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],  # OPTIONSやPOSTを許可
    allow_headers=["*"],
)

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

# Google Sheets API の認証
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("winged-acolyte-462314-f0-a9815c766376.json", scope)
client = gspread.authorize(creds)

# スプレッドシートを開く
spreadsheet = client.open("問い合わせ一覧")
sheet = spreadsheet.sheet1

@app.post("/contact")
def receive_contact(form: ContactForm):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([form.name, form.email, form.message, now])
    return {"message": "スプレッドシートに保存しました！"}
