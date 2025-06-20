from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    question: str = Field(..., description="사용자의 질문")
    session_id: str = Field(..., description="세션 ID")
    keepgoing: bool = Field(default=True, description="기존 세션 유지 여부")
    user_display: str = Field(default="🙋‍♀️ 사용자", description="사용자 표시명")