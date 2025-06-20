#!/bin/bash

echo "🚀 Notion Chat Lambda 배포 시작..."

# 1. 가상환경 활성화
source venv/bin/activate

# 2. 환경변수 기반으로 zappa_settings.json 생성
echo "⚙️  환경변수 로딩 및 zappa_settings.json 생성..."
python gen_zappa_env.py

# 3. Zappa 배포
echo "📦 Lambda 함수 배포 중..."
if [ "$1" = "initial" ]; then
    echo "🆕 초기 배포..."
    zappa deploy production
else
    echo "🔄 업데이트 배포..."
    zappa update production
fi

echo "✅ 배포 완료!" 