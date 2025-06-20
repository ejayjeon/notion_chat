# In-memory 세션 저장소

session_map = {}

def get_or_create_session(session_id: str, create_func) -> str:
    if session_id in session_map:
        return session_map[session_id]
    else:
        new_page_id = create_func()
        session_map[session_id] = new_page_id
        return new_page_id