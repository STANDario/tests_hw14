import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.schemas import RequestPassword
from src.database.models import User
from src.repository.users import update_password, update_avatar, get_user_by_email_for_confirm


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, username="user", email="test@test.com", password="password")

    async def test_get_user_by_email_for_confirm(self):
        self.session.query(User).filter().first.return_value = self.user
        result = await get_user_by_email_for_confirm("test@test.com", self.session)
        self.assertEqual(result, self.user)

    async def test_update_avatar_and_password(self):
        self.session.query(User).filter().first.return_value = self.user
        result_avatar = await update_avatar("test@test.com", "url.com", self.session)
        result_password = await update_password("test@test.com", RequestPassword(password="password"), self.session)
        self.assertEqual(result_avatar, self.user)
        self.assertEqual(result_password, self.user)


if __name__ == '__main__':
    unittest.main()