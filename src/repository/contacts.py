from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel
from src.database.models import User


async def get_contacts(limit: int, skip: int, user: User, db: Session):
    """
    Retrieves a list of contacts for a specific user from the database.

    :param limit: The maximum number of contacts to retrieve.
    :type limit: int
    :param skip: The number of contacts to skip before starting to return items.
    :type skip: int
    :param user: The user for whom to retrieve contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts for the specified user.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter_by(user_id=user.id).limit(limit).offset(skip).all()


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
    Retrieves a contact by its ID for a specific user from the database.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user for whom to retrieve the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID for the given user, or None if not found.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def get_contact_by_email(contact_email: str, user: User, db: Session):
    """
    Retrieves a contact by its email address for a specific user from the database.

    :param contact_email: The email address of the contact to retrieve.
    :type contact_email: str
    :param user: The user for whom to retrieve the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified email address for the given user, or None if not found.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.email == contact_email, Contact.user_id == user.id)).first()


async def get_contact_by_name(contact_name: str, user: User, db: Session):
    """
    Retrieves contacts by name for a specific user from the database.

    :param contact_name: The name of the contacts to retrieve.
    :type contact_name: str
    :param user: The user for whom to retrieve the contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with the specified name for the given user, or an empty list if none are found.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(and_(Contact.first_name == contact_name, Contact.user_id == user.id)).all()


async def get_contact_by_surname(contact_surname: str, user: User, db: Session):
    """
    Retrieves contacts by surname for a specific user from the database.

    :param contact_surname: The surname of the contacts to retrieve.
    :type contact_surname: str
    :param user: The user for whom to retrieve the contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with the specified surname for the given user, or an empty list if none are found.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(and_(Contact.surname == contact_surname, Contact.user_id == user.id)).all()


async def get_contact_by_phone(phone: str, user: User, db: Session):
    """
    Retrieves a contact by phone number for a specific user from the database.

    :param phone: The phone number of the contact to retrieve.
    :type phone: str
    :param user: The user for whom to retrieve the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified phone number for the given user, or None if not found.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.phone_number == phone, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session):
    """
    Creates a new contact for a specific user in the database.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param user: The user for whom to create the contact.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, db: Session, user: User, contact_id: int):
    """
    Updates an existing contact for a specific user in the database.

    :param body: The updated data for the contact.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param user: The user to whom the contact belongs.
    :type user: User
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :return: The updated contact if found, otherwise None.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        contact.first_name = body.first_name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session):
    """
    Removes an existing contact for a specific user from the database.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to whom the contact belongs.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact if found, otherwise None.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_birthday_contact(user: User, db: Session):
    """
    Retrieves contacts with upcoming birthdays for a specific user from the database.

    :param user: The user for whom to retrieve contacts.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with birthdays within the next 7 days.
    :rtype: List[Contact]
    """
    contacts = db.query(Contact).filter_by(user_id=user.id).all()
    contacts_result = []
    today = datetime.now().date()
    if contacts:
        for contact in contacts:
            contact_birthday = contact.birthday.replace(year=datetime.now().year)
            maybe_seven_days = (contact_birthday - today).days
            if 0 <= maybe_seven_days <= 7:
                contacts_result.append(contact)
    if contacts_result:
        return contacts_result
    else:
        return None
