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
        # API Key 확인 (Base64 디코딩 처리)
        api_key = request.headers.get("X-API-KEY")
        print(f"Received API key: {api_key}")
        
        # 받은 API 키가 Base64 인코딩되어 있다면 디코딩
        try:
            import base64
            decoded_api_key = base64.b64decode(api_key).decode('utf-8')
            print(f"Decoded API key: {decoded_api_key}")
        except:
            decoded_api_key = api_key  # 디코딩 실패 시 원본 사용
            print(f"Using original API key: {decoded_api_key}")
        
        print(f"Expected API key: {BACKEND_API_KEY}")
        
        if decoded_api_key != BACKEND_API_KEY:
            return jsonify({"error": "❌ 인증 실패: 유효하지 않은 API 키입니다"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400

        # message와 question 둘 다 지원
        question = data.get("question", data.get("message", "")).strip()
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
        question_blocks = [create_callout_block(f"질문: {question}", emoji=user_display)]
        append_blocks_to_page(page_id, question_blocks)

        # GPT 응답 (새로운 API 사용)
        # OpenAI API 키 설정 (디코딩된 값 사용)
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}],
        )
        answer = response.choices[0].message.content.strip()

        # 응답 기록 (답변 콜아웃 + 마크다운 파싱된 블록들)
        answer_blocks = [create_callout_block("답변", emoji="🤖")]
        answer_blocks.extend(parse_gpt_response(answer))
        append_blocks_to_page(page_id, answer_blocks)

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