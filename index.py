import openai
import os
import time
from datetime import datetime
from loading_animation import LoadingAnimation
from notion_blocks_custom import (
    create_callout_block,
    parse_gpt_response,
    append_blocks_to_page,
)

# --- 설정 ---

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = "217fefc5f0b080fd894dfae62a105304"

openai.api_key = OPENAI_API_KEY

import requests

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


# --- 기능 구현 ---

def ask_gpt(question: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content.strip()


def create_conversation_page(title: str) -> str:
    url = "https://api.notion.com/v1/pages"
    today = datetime.now().strftime("%Y-%m-%d")

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "날짜": {"date": {"start": today}},
            "질문": {"title": [{"text": {"content": title}}]}
        }
    }

    response = requests.post(url, headers=NOTION_HEADERS, json=data)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print("❌ 페이지 생성 실패:", response.json())
        raise RuntimeError("Notion 페이지 생성 실패")


# def loading_animation():
#     print("⏳ 답변 생성 중", end="", flush=True)
#     for _ in range(3):
#         time.sleep(0.5)
#         print(".", end="", flush=True)
#     print("")


def chat_loop():
    print("💬 GPT + Notion 대화 기록기 시작 (종료하려면 'exit' 입력)")
    session_page_id = None
    

    while True:
        question = input("\n🙋‍♀️ 예삐의 질문: ").strip()
        if question.lower() in ["exit", "quit", "종료"]:
            print("👋 대화를 종료합니다.")
            break

        if session_page_id is None:
            session_page_id = create_conversation_page(title=question)

        # 질문 → 콜아웃 블록으로 추가
        append_blocks_to_page(session_page_id, [create_callout_block(question, emoji="🙋‍♀️")])

        # 🔄 로딩 애니메이션
        loader = LoadingAnimation()
        loader.start()

        try:
            answer = ask_gpt(question)
        finally:
            loader.stop() 
        # GPT 응답 → 문단/코드 블록으로 변환 후 추가
        blocks = parse_gpt_response(answer)
        append_blocks_to_page(session_page_id, blocks)

        print("\n📜 GPT 응답:\n", answer)


# --- 실행 ---

if __name__ == "__main__":
    if not OPENAI_API_KEY or not NOTION_API_KEY:
        print("❌ 환경변수가 누락되었습니다. .zshrc 또는 .env 파일을 확인하세요.")
    else:
        chat_loop()