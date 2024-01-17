from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactResponse, ContactModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from src.database.models import User


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(limit: int = Query(default=10, le=50), skip: int = 0, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(limit, skip, current_user, db)
    return contacts


@router.get("/search_by_email", response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_email(contact_email: str, db: Session = Depends(get_db),
                               current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_email(contact_email, current_user, db)
    return contact


@router.get("/search_by_name", response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_name(contact_name: str, db: Session = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_name(contact_name, current_user, db)
    return contact


@router.get("/search_by_surname", response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_surname(contact_surname: str, db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_surname(contact_surname, current_user, db)
    return contact


@router.get("/birthday", response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_birthday_contact(db: Session = Depends(get_db),
                               current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_birthday_contact(current_user, db)
    return contact


@router.get("/{contact_id}", response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact_by_phone(body.phone_number, current_user, db)
    print(contact)
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact with this number already exists!")
    contact = await repository_contacts.create_contact(body, current_user, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(body, db, current_user, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact


@router.delete("/{contact_id}", dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return contact
