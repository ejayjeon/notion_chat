import os
from dotenv import load_dotenv
import base64

# .env 파일 자동 로드
load_dotenv()

# 환경변수
encoded_openai_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = base64.b64decode(encoded_openai_key).decode('utf-8') # OpenAI API 키 (base64 디코딩)

encoded_notion_key = os.getenv("NOTION_API_KEY")
NOTION_API_KEY = base64.b64decode(encoded_notion_key).decode('utf-8') # Notion API 키 (base64 디코딩)

NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
# BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")
encoded_backend_key = os.getenv("BACKEND_API_KEY")
BACKEND_API_KEY = base64.b64decode(encoded_backend_key).decode('utf-8') # Proxy -> GPT API 서버의 문을 여는 열쇠? (base64 디코딩)

# OpenAI API 설정
import openai
openai.api_key = OPENAI_API_KEY

# Notion 공통 헤더
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}