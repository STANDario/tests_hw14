import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from src.database.models import User
from src.schemas import UserModel
from src.repository.auth import get_user_by_email, create_user


class TestAuth(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(username="user", email="test@test.com", password="password")

    async def test_get_user_by_email(self):
        self.session.query(self.user).filter_by(self.user.email).first.return_value = self.user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        body = UserModel(
            username="user",
            email="test@test.com",
            password="password"
        )
        g = Gravatar(body.email)
        user = User(**body.model_dump(), avatar=g.get_image())
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, user.username)
        self.assertTrue(hasattr(result, "id"))


if __name__ == '__main__':
    unittest.main()
