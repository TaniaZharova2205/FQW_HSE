from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")

        if not re.search(r"[a-z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")

        if not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")

        if not re.search(r"[^\w\s]", value):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")

        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str