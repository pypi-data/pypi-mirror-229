from hyfi.composer import BaseModel


class ChatMessage(BaseModel):
    role: str = "user"
    content: str
