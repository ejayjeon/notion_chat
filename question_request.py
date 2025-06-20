from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    session_id: str
    keepgoing: bool = True
    user_display: str = "🙋‍♀️ 사용자"