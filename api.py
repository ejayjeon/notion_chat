# from flask import Flask, request, jsonify
from fastapi import FastAPI, Request, Header, HTTPException
from mangum import Mangum
from question_request import QuestionRequest
from config import (
    OPENAI_API_KEY,
    NOTION_API_KEY,
    BACKEND_API_KEY,
    NOTION_DATABASE_ID,
    NOTION_HEADERS,
)
from session_store import get_or_create_session
import openai
import requests
from datetime import datetime
from notion_blocks_custom import (
    create_conversation_page,
    create_callout_block,
    parse_gpt_response,
    append_blocks_to_page,
)

app = FastAPI()

# --- 기능 구현 ---

@app.get("/")
def read_root():
    return {"message": "Hello from Lambda!"}

handler = Mangum(app)

@app.post("/ask")
async def ask(req: QuestionRequest, x_api_key: str = Header(..., alias="X-API-KEY")):
    if x_api_key != BACKEND_API_KEY:
        raise HTTPException(status_code=401, detail="❌ 인증 실패: 유효하지 않은 API 키입니다")

    question = req.question.strip()
    if not question:
        return {"error": "질문이 비어 있습니다"}

    # 세션에 따른 페이지 관리
    page_id = (
    get_or_create_session(req.session_id, lambda: create_conversation_page(req.question))
    if req.keepgoing else create_conversation_page(req.question)
)

    # 질문 기록 (콜아웃 블록)
    append_blocks_to_page(page_id, [create_callout_block(req.question, emoji=req.user_display)])

    # GPT 응답
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": question}],
    )
    answer = response.choices[0].message.content.strip()

    # 응답 기록 (문단 + 코드 블록 자동 분리)
    blocks = parse_gpt_response(answer)
    append_blocks_to_page(page_id, blocks)

    return {"answer": answer, "session_page_id": page_id}


# def chat_loop():
#     print("💬 GPT + Notion 대화 기록기 시작 (종료하려면 'exit' 입력)")
#     session_page_id = None
    

#     while True:
#         question = input("\n🙋‍♀️ 예삐의 질문: ").strip()
#         if question.lower() in ["exit", "quit", "종료"]:
#             print("👋 대화를 종료합니다.")
#             break

#         if session_page_id is None:
#             session_page_id = create_conversation_page(title=question)

#         # 질문 → 콜아웃 블록으로 추가
#         append_blocks_to_page(session_page_id, [create_callout_block(question, emoji="🙋‍♀️")])

#         # 🔄 로딩 애니메이션
#         loader = LoadingAnimation()
#         loader.start()

#         try:
#             answer = ask_gpt(question)
#         finally:
#             loader.stop() 
#         # GPT 응답 → 문단/코드 블록으로 변환 후 추가
#         blocks = parse_gpt_response(answer)
#         append_blocks_to_page(session_page_id, blocks)

#         print("\n📜 GPT 응답:\n", answer)


# --- 실행 ---
# Serverless 환경에서는 내부적으로 FastAPI 객체(app)만 찾고 실행합니다
# uvicorn.run(...) 같은 코드는 자동 실행됩니다

# 로컬 테스트 용 
if __name__ == "__main__":
    if not OPENAI_API_KEY or not NOTION_API_KEY:
        print("❌ 환경변수가 누락되었습니다. .zshrc 또는 .env 파일을 확인하세요.")
    else:
        import uvicorn
        # chat_loop()
        uvicorn.run("api:app", host="0.0.0.0", port=5051, reload=True)