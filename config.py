import os
from dotenv import load_dotenv
import base64

# .env 파일 자동 로드 (로컬 개발용)
load_dotenv()

def safe_decode_base64(encoded_value, var_name):
    """Base64 디코딩을 안전하게 수행"""
    if not encoded_value:
        print(f"Warning: {var_name} 환경변수가 설정되지 않았습니다.")
        return None
    
    try:
        # "-" 체크 (Zappa 기본값)
        if encoded_value == "-":
            print(f"Warning: {var_name}가 기본값('-')으로 설정되어 있습니다.")
            return None
        
        # Base64 디코딩 시도
        try:
            decoded = base64.b64decode(encoded_value).decode('utf-8')
            return decoded
        except:
            # Base64 디코딩 실패 시 원본 값 반환 (평문일 가능성)
            print(f"Info: {var_name} 평문으로 사용")
            return encoded_value
            
    except Exception as e:
        print(f"Error processing {var_name}: {str(e)}")
        return None

# 환경변수 안전하게 로드
try:
    print("환경변수 로딩 시작...")
    
    encoded_openai_key = os.getenv("OPENAI_API_KEY")
    OPENAI_API_KEY = safe_decode_base64(encoded_openai_key, "OPENAI_API_KEY")

    encoded_notion_key = os.getenv("NOTION_API_KEY") 
    NOTION_API_KEY = safe_decode_base64(encoded_notion_key, "NOTION_API_KEY")

    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
    if not NOTION_DATABASE_ID or NOTION_DATABASE_ID == "-":
        print("Warning: NOTION_DATABASE_ID 환경변수가 설정되지 않았습니다.")
        NOTION_DATABASE_ID = None

    encoded_backend_key = os.getenv("BACKEND_API_KEY")
    BACKEND_API_KEY = safe_decode_base64(encoded_backend_key, "BACKEND_API_KEY")

    # OpenAI API 설정
    import openai
    # 환경변수 체크
    if not OPENAI_API_KEY:
        print("Warning: OpenAI API 키가 없습니다. OpenAI 기능이 제한됩니다.")

    # Notion 공통 헤더
    if NOTION_API_KEY:
        NOTION_HEADERS = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
    else:
        print("Warning: Notion API 키가 없습니다. Notion 기능이 제한됩니다.")
        NOTION_HEADERS = {}

    print("환경변수 로딩 완료")

except Exception as e:
    print(f"환경변수 설정 중 오류 발생: {str(e)}")
    # Lambda에서는 기본값으로 설정
    OPENAI_API_KEY = None
    NOTION_API_KEY = None
    NOTION_DATABASE_ID = None
    BACKEND_API_KEY = None
    NOTION_HEADERS = {}