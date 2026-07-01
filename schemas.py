from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr

# Базова схема зі спільними полями
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_data: Optional[str] = None

# Схема для створення контакту
class ContactCreate(ContactBase):
    pass

# Схема для оновлення контакту
class ContactUpdate(ContactBase):
    pass

# Схема для відповіді API (містить ID)
class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True  # Для сумісності з ORM SQLAlchemy
