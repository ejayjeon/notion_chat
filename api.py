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

        # GPT 응답 (더 빠른 모델 사용으로 타임아웃 방지)
        # OpenAI API 키 설정 (디코딩된 값 사용)
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "간결하고 명확한 답변을 제공하세요. 코드가 필요하면 마크다운 형식으로 작성하세요."},
                {"role": "user", "content": question}
            ],
            max_tokens=1000,  # 응답 길이 제한으로 타임아웃 방지
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()

        # 모든 블록을 한 번에 추가 (성능 최적화)
        all_blocks = []
        # 질문 블록
        all_blocks.append(create_callout_block(question, emoji=user_display))
        # 답변 헤더 블록 
        all_blocks.append(create_callout_block("답변", emoji="🤖"))
        # 답변 내용 블록들
        all_blocks.extend(parse_gpt_response(answer))
        
        # 한 번에 모든 블록 추가
        append_blocks_to_page(page_id, all_blocks)

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