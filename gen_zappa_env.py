import json
from dotenv import dotenv_values

ZAPPA_TEMPLATE_PATH = "zappa_settings_template.json"

# 1. .env 로딩
env_vars = dotenv_values(".env")

# 2. 템플릿 파일 로딩
with open(ZAPPA_TEMPLATE_PATH, "r") as f:
    zappa_settings = json.load(f)

# 3. 템플릿에 환경변수 추가
zappa_settings["production"]["environment_variables"] = env_vars

# 4. 실제 zappa_settings.json 생성
with open(ZAPPA_SETTINGS_PATH, "w") as f:
    json.dump(zappa_settings, f, indent=2)

print("✅ zappa_settings.json 생성 완료!")