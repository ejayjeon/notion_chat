# GPT + Notion 채팅 기록기 📘💬

OpenAI GPT-4와 채팅하면서 대화 내용을 실시간으로 Notion 데이터베이스에 자동 저장하는 Python 프로그램입니다.

## 🚀 주요 기능

- **GPT-4와 실시간 대화**: 터미널에서 GPT-4와 자연스럽게 대화
- **Notion 자동 기록**: 질문과 답변이 자동으로 Notion 페이지에 저장
- **다양한 블록 지원**: GPT 응답을 마크다운 문법에 따라 적절한 Notion 블록으로 변환
  - 제목 (`#`, `##`, `###`)
  - 코드 블록 (```) 및 인라인 코드 (`code`)
  - 리스트 (`-`, `1.`)
  - 체크박스 (`- [ ]`, `- [x]`)
  - 인용문 (`> 내용`)
  - 구분선 (`---`)
  - 토글 (`::toggle 내용`)
- **로딩 애니메이션**: 답변 생성 중 시각적 피드백 제공
- **세션 관리**: 하나의 대화 세션이 하나의 Notion 페이지로 기록

## 📋 필수 조건

- Python 3.9 이상
- OpenAI API 키
- Notion API 키 및 데이터베이스 설정

## 🛠 설치 방법

### 1. 패키지 설치

```bash
pip install openai requests
```

### 2. API 키 설정

다음 환경변수를 설정해야 합니다:

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export OPENAI_API_KEY="your_openai_api_key_here"
export NOTION_API_KEY="your_notion_api_key_here"
```

### 3. Notion 데이터베이스 설정

1. Notion에서 새 데이터베이스 생성
2. 다음 속성을 가진 데이터베이스를 만드세요:
   - `날짜` (Date 타입)
   - `질문` (Title 타입)
3. 데이터베이스 ID를 복사하여 `index.py`의 `NOTION_DATABASE_ID` 변수에 설정

### 4. Notion 통합(Integration) 설정

1. [Notion Developers](https://developers.notion.com)에서 새 통합 생성
2. 생성된 Internal Integration Token을 복사
3. 위에서 만든 데이터베이스에 통합 권한 부여:
   - 데이터베이스 페이지 → 우상단 점 세 개 → 연결 추가 → 통합 선택

## 🚀 사용법

### 기본 실행

```bash
python index.py
```

### 대화 예시

```
💬 GPT + Notion 대화 기록기 시작 (종료하려면 'exit' 입력)

🙋‍♀️ 예삐의 질문: Python에서 리스트와 튜플의 차이점을 알려줘

⏳ 답변 생성 중.....

📜 GPT 응답:
 # Python 리스트와 튜플의 차이점

## 1. 가변성 (Mutability)

**리스트 (List)**
- 가변(mutable) 객체
- 생성 후 요소 추가, 삭제, 수정 가능

```python
my_list = [1, 2, 3]
my_list.append(4)  # [1, 2, 3, 4]
```

**튜플 (Tuple)**
- 불변(immutable) 객체
- 생성 후 요소 변경 불가능

```python
my_tuple = (1, 2, 3)
# my_tuple.append(4)  # 에러 발생!
```

🙋‍♀️ 예삐의 질문: exit
👋 대화를 종료합니다.
```

### 명령어

- **일반 질문**: 평상시처럼 질문을 입력하세요
- **종료**: `exit`, `quit`, 또는 `종료` 입력

## 📁 파일 구조

```
notion_chat/
├── index.py                 # 메인 실행 파일
├── notion_blocks_custom.py  # Notion 블록 생성 및 마크다운 파싱
├── loading_animation.py     # 로딩 애니메이션 구현
└── README.md               # 이 파일
```

## 🔧 주요 기능 설명

### 1. `index.py`
- GPT API 호출 및 사용자 인터페이스
- Notion 페이지 생성 및 관리
- 대화 세션 루프 실행

### 2. `notion_blocks_custom.py`
- GPT 응답을 Notion 블록으로 변환
- 마크다운 문법 파싱 (코드 블록, 제목, 리스트 등)
- Notion API를 통한 블록 추가

### 3. `loading_animation.py`
- 비동기 로딩 애니메이션 표시
- 사용자 경험 개선

## 🎨 지원하는 마크다운 문법

| 문법 | Notion 블록 타입 | 예시 |
|------|------------------|------|
| `# 제목` | Heading 1 | `# 대제목` |
| `## 제목` | Heading 2 | `## 중제목` |
| `### 제목` | Heading 3 | `### 소제목` |
| ````code```` | Code Block | ````python\nprint("hello")\n```` |
| `code` | Inline Code | `print()` 함수 |
| `- 항목` | Bullet List | `- 첫 번째 항목` |
| `1. 항목` | Numbered List | `1. 첫 번째 항목` |
| `- [ ] 할일` | Todo (unchecked) | `- [ ] 완료되지 않음` |
| `- [x] 할일` | Todo (checked) | `- [x] 완료됨` |
| `> 인용` | Quote | `> 중요한 말` |
| `---` | Divider | `---` |
| `::toggle 내용` | Toggle | `::toggle 접을 수 있는 내용` |

## ⚙️ 설정 변경

### 데이터베이스 ID 변경
`index.py` 파일의 12번째 줄에서 변경:
```python
NOTION_DATABASE_ID = "your_database_id_here"
```

### GPT 모델 변경
`ask_gpt()` 함수에서 모델 변경 가능:
```python
response = openai.ChatCompletion.create(
    model="gpt-4",  # 또는 "gpt-3.5-turbo"
    messages=[{"role": "user", "content": question}],
)
```

## 🐛 문제 해결

### 환경변수 오류
```
❌ 환경변수가 누락되었습니다. .zshrc 또는 .env 파일을 확인하세요.
```
- OpenAI API 키와 Notion API 키가 올바르게 설정되었는지 확인
- 터미널을 재시작하여 환경변수 적용

### Notion 페이지 생성 실패
```
❌ 페이지 생성 실패
```
- Notion 데이터베이스 ID가 올바른지 확인
- Notion 통합이 해당 데이터베이스에 권한을 가지고 있는지 확인
- 데이터베이스 속성 (`날짜`, `질문`)이 올바르게 설정되었는지 확인

## 📝 라이선스

이 프로젝트는 개인 및 교육 목적으로 자유롭게 사용할 수 있습니다.

## 🤝 기여

버그 리포트나 기능 제안은 언제든 환영합니다!
