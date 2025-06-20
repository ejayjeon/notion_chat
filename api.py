from flask import Flask, request, jsonify
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

app = Flask(__name__)

# --- 기능 구현 ---

@app.route("/", methods=["GET"])
def read_root():
    return {"message": "Hello from Lambda!", "status": "healthy"}

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # API Key 확인
        api_key = request.headers.get("X-API-KEY")
        if api_key != BACKEND_API_KEY:
            return jsonify({"error": "❌ 인증 실패: 유효하지 않은 API 키입니다"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400

        question = data.get("question", "").strip()
        session_id = data.get("session_id")
        keepgoing = data.get("keepgoing", False)
        user_display = data.get("user_display", "🙋‍♀️")

        if not question:
            return jsonify({"error": "질문이 비어 있습니다"}), 400

        # 세션에 따른 페이지 관리
        page_id = (
            get_or_create_session(session_id, lambda: create_conversation_page(question))
            if keepgoing else create_conversation_page(question)
        )

        # 질문 기록 (콜아웃 블록)
        append_blocks_to_page(page_id, [create_callout_block(question, emoji=user_display)])

        # GPT 응답 (새로운 API 사용)
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": question}],
        )
        answer = response.choices[0].message.content.strip()

        # 응답 기록 (문단 + 코드 블록 자동 분리)
        blocks = parse_gpt_response(answer)
        append_blocks_to_page(page_id, blocks)

        return jsonify({"answer": answer, "session_page_id": page_id})
    
    except Exception as e:
        print(f"Error in ask endpoint: {str(e)}")
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500

# 로컬 테스트용
if __name__ == "__main__":
    if not OPENAI_API_KEY or not NOTION_API_KEY:
        print("❌ 환경변수가 누락되었습니다. .zshrc 또는 .env 파일을 확인하세요.")
    else:
        app.run(host="0.0.0.0", port=5051, debug=True) 