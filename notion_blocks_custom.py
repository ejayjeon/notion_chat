import requests
import os
import re
from datetime import datetime
from config import NOTION_API_KEY, NOTION_DATABASE_ID

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}
NOTION_CODE_LANGUAGES = {
    "python", "javascript", "bash", "html", "css", "json", "java", "c", "c++", "c#", "markdown",
    "typescript", "yaml", "sql", "swift", "go", "ruby", "rust", "plain text", "shell", "php",
    "kotlin", "dart", "vb.net", "xml", "scss", "lua", "perl", "r", "haskell", "scala", "elixir"
}

DIVIDER_RE = re.compile(r"^[-*_]{3,}$")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")

# --- Notion 페이지 생성 ---
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

def create_code_block(content: str, language: str = "python"):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "language": language,
        },
    }

def create_paragraph(content: str):
    matches = INLINE_CODE_RE.finditer(content)
    rich_text = []
    last_index = 0
    for match in matches:
        start, end = match.span()
        if start > last_index:
            rich_text.append({"type": "text", "text": {"content": content[last_index:start]}})
        rich_text.append({
            "type": "text",
            "text": {"content": match.group(1)},
            "annotations": {"code": True}
        })
        last_index = end
    if last_index < len(content):
        rich_text.append({"type": "text", "text": {"content": content[last_index:]}})
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text},
    }

def create_callout_block(content: str, emoji: str = "❓"):
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "icon": {"type": "emoji", "emoji": emoji},
        },
    }

def create_heading_block(content: str, level: int = 3):
    heading_type = {
        1: "heading_1",
        2: "heading_2",
        3: "heading_3"
    }.get(level, "heading_3")
    return {
        "object": "block",
        "type": heading_type,
        heading_type: {
            "rich_text": [{"type": "text", "text": {"content": content}}]
        }
    }

def create_toggle_block(content: str):
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "children": []
        }
    }

def create_bulleted_list_item(content: str):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
        },
    }

def create_numbered_list_item(content: str):
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
        },
    }

def create_to_do_item(content: str, checked: bool = False):
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
            "checked": checked
        },
    }

def create_quote_block(content: str):
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": [{"type": "text", "text": {"content": content}}],
        },
    }

def create_divider_block():
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }

def sanitize_language(lang: str):
    l = lang.strip().lower()
    return l if l in NOTION_CODE_LANGUAGES else "plain text"

def parse_gpt_response(response: str):
    blocks = []
    lines = response.split("\n")
    code_mode = False
    code_lines = []

    for line in lines:
        line = line.rstrip()
        if line.strip().startswith("```") and not code_mode:
            code_mode = True
            code_language = sanitize_language(line.strip().replace("```", "").strip())
            code_lines = []
        elif line.strip() == "```" and code_mode:
            blocks.append(create_code_block("\n".join(code_lines), code_language))
            code_mode = False
        elif code_mode:
            code_lines.append(line)
        elif line.startswith("### "):
            blocks.append(create_heading_block(line[4:], level=3))
        elif line.startswith("## "):
            blocks.append(create_heading_block(line[3:], level=2))
        elif line.startswith("# "):
            blocks.append(create_heading_block(line[2:], level=1))
        elif line.startswith("::toggle "):
            blocks.append(create_toggle_block(line.replace("::toggle ", "")))
        elif line.startswith("- [ ] "):
            blocks.append(create_to_do_item(line[6:], checked=False))
        elif line.startswith("- [x] ") or line.startswith("- [X] "):
            blocks.append(create_to_do_item(line[6:], checked=True))
        elif line.startswith("- "):
            blocks.append(create_bulleted_list_item(line[2:]))
        elif re.match(r"\d+\. ", line):
            blocks.append(create_numbered_list_item(line.partition(". ")[2]))
        elif line.startswith("> "):
            blocks.append(create_quote_block(line[2:]))
        elif DIVIDER_RE.match(line.strip()):
            blocks.append(create_divider_block())
        elif line.strip() == "":
            continue
        else:
            blocks.append(create_paragraph(line))

    return blocks

def append_blocks_to_page(page_id: str, blocks: list):
    """한 번에 모든 블록을 추가하여 성능 최적화"""
    if not blocks:
        return
    
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    # Notion API는 한 번에 최대 100개 블록까지 추가 가능
    batch_size = 100
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        response = requests.patch(url, headers=NOTION_HEADERS, json={"children": batch})
        if response.status_code != 200:
            print(f"❌ 블록 추가 실패 (배치 {i//batch_size + 1}):", response.json())
            # 실패 시 개별적으로 다시 시도
            for block in batch:
                individual_response = requests.patch(url, headers=NOTION_HEADERS, json={"children": [block]})
                if individual_response.status_code != 200:
                    print(f"❌ 개별 블록 추가 실패:", individual_response.json())