from sqlalchemy.orm import Session

from src.schemas import RequestPassword
from src.database.models import User


async def get_user_by_email_for_confirm(contact_email: str, db: Session):
    """
    Retrieves a user by email for the purpose of email confirmation from the database.

    :param contact_email: The email address of the user to retrieve.
    :type contact_email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email address for email confirmation, or None if not found.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == contact_email).first()


async def confirmed_email(email: str, db: Session):
    """
    Confirms the email address for a user in the database.

    :param email: The email address of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    """
    user = await get_user_by_email_for_confirm(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session):
    """
    Updates the avatar for a user in the database.

    :param email: The email address of the user whose avatar to update.
    :type email: str
    :param url: The new avatar URL to set.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user.
    :rtype: User
    """
    user = await get_user_by_email_for_confirm(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(email: str, password: RequestPassword, db: Session):
    """
    Updates the password for a user in the database.

    :param email: The email address of the user whose password to update.
    :type email: str
    :param password: The new password to set.
    :type password: RequestPassword
    :param db: The database session.
    :type db: Session
    :return: The updated user.
    :rtype: User
    """
    user = await get_user_by_email_for_confirm(email, db)
    user.password = password
    db.commit()
    return user
