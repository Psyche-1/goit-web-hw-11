from datetime import date, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy import select, or_, extract
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

# Створення таблиць у БД при запуску
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts REST API")

# --- CRUD Операції ---

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    # Перевірка унікальності Email
    db_contact = db.execute(select(models.Contact).filter_by(email=contact.email)).scalar_one_or_none()
    if db_contact:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_contact = models.Contact(**contact.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@app.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_contacts(
    search: Optional[str] = Query(None, description="Search by first name, last name or email"),
    db: Session = Depends(get_db)
):
    query = select(models.Contact)
    if search:
        query = query.filter(
            or_(
                models.Contact.first_name.ilike(f"%{search}%"),
                models.Contact.last_name.ilike(f"%{search}%"),
                models.Contact.email.ilike(f"%{search}%")
            )
        )
    return db.scalars(query).all()

@app.get("/contacts/upcoming-birthdays/", response_model=List[schemas.ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    upcoming_contacts = []
    
    # Отримуємо всі контакти (для великих БД краще оптимізувати через SQL extract)
    all_contacts = db.scalars(select(models.Contact)).all()
    
    for contact in all_contacts:
        # Визначаємо день народження у поточному році
        try:
            bday_this_year = contact.birthday.replace(year=today.year)
        except ValueError:
            # Обробка для 29 лютого у невисокосний рік
            bday_this_year = contact.birthday.replace(year=today.year, day=28)
            
        # Якщо день народження вже минув, перевіряємо наступний рік
        if bday_this_year < today:
            try:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            except ValueError:
                bday_this_year = bday_this_year.replace(year=today.year + 1, day=28)
                
        # Перевіряємо чи входить дата в проміжок 7 днів
        if today <= bday_this_year <= today + timedelta(days=7):
            upcoming_contacts.append(contact)
            
    return upcoming_contacts

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.get(models.Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, updated_contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    contact = db.get(models.Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    for key, value in updated_contact.model_dump().items():
        setattr(contact, key, value)
        
    db.commit()
    db.refresh(contact)
    return contact

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.get(models.Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return None
