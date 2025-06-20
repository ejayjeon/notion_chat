import json
from dotenv import dotenv_values

ZAPPA_SETTINGS_PATH = "zappa_settings.json"

# 1. .env 로딩
env_vars = dotenv_values(".env")

# 2. 기존 zappa_settings.json 로딩
with open(ZAPPA_SETTINGS_PATH, "r") as f:
    zappa_settings = json.load(f)

# 3. 기존 설정에 새로운 환경변수 추가
zappa_settings["production"]["environment_variables"] = env_vars

# 4. 수정된 설정 저장
with open(ZAPPA_SETTINGS_PATH, "w") as f:
    json.dump(zappa_settings, f, indent=2)