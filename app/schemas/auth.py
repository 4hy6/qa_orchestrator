from app.schemas.common import BaseSchema


class AuthRequest(BaseSchema):
    username: str
    password: str


class AuthResponse(BaseSchema):
    token: str
