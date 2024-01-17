from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieves a user from the database based on the provided email.

    :param email: The email address of the user to search for.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email if found, otherwise None.
    :rtype: User | None
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    """
    Creates a new user in the database.

    :param body: The data for the user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    g = Gravatar(body.email)

    new_user = User(**body.model_dump(), avatar=g.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    Updates the refresh token for a specific user in the database.

    :param user: The user for whom to update the refresh token.
    :type user: User
    :param refresh_token: The new refresh token to set.
    :param db: The database session.
    :type db: Session
    """
    user.refresh_token = refresh_token
    db.commit()
