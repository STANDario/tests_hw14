from datetime import date, datetime
import sys
import os
from pathlib import Path

import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    get_contact_by_email,
    get_contact_by_name,
    get_contact_by_surname,
    get_contact_by_phone,
    create_contact,
    update_contact,
    remove_contact,
    get_birthday_contact
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, username="user", email="test@test.com", password="password")

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query(Contact).filter_by().limit().offset().all.return_value = contacts
        result = await get_contacts(10, 0, self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact()
        self.session.query(Contact).filter().first.return_value = contact
        result_id = await get_contact_by_id(1, self.user, self.session)
        result_email = await get_contact_by_email("test@test.com", self.user, self.session)
        result_phone = await get_contact_by_phone("380671125303", self.user, self.session)
        self.assertEqual(result_id, contact)
        self.assertEqual(result_email, contact)
        self.assertEqual(result_phone, contact)

    async def test_get_contact_not_found(self):
        self.session.query(Contact).filter().first.return_value = None
        result_id = await get_contact_by_id(1, self.user, self.session)
        result_email = await get_contact_by_email("test@test.com", self.user, self.session)
        result_phone = await get_contact_by_phone("380671125303", self.user, self.session)
        self.assertIsNone(result_id)
        self.assertIsNone(result_email)
        self.assertIsNone(result_phone)

    async def test_get_contact_by_name_surname(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query(Contact).filter().all.return_value = contacts
        result_name = await get_contact_by_name("username", self.user, self.session)
        result_surname = await get_contact_by_surname("surname", self.user, self.session)
        self.assertEqual(result_name, contacts)
        self.assertEqual(result_surname, contacts)

    async def test_get_contact_by_name_surname_not_found(self):
        self.session.query(Contact).filter().all.return_value = None
        result_name = await get_contact_by_name("username", self.user, self.session)
        result_surname = await get_contact_by_surname("surname", self.user, self.session)
        self.assertIsNone(result_name)
        self.assertIsNone(result_surname)

    async def test_create_contact(self):
        body = ContactModel(first_name="Andrii",
                            surname="Bugay",
                            email="test@test.com",
                            phone_number="380934267600",
                            birthday=date(year=2002, month=11, day=22))
        result = await create_contact(body, self.user, self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact(self):
        body = ContactModel(first_name="Andrii",
                            surname="Bugay",
                            email="test@test.com",
                            phone_number="380934267600",
                            birthday=date(year=2002, month=11, day=22))
        contact = Contact()
        self.session.query(Contact).filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(body, self.session, self.user, 1)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(first_name="Andrii",
                            surname="Bugay",
                            email="test@test.com",
                            phone_number="380934267600",
                            birthday=date(year=2002, month=11, day=22))
        contact = Contact()
        self.session.query(Contact).filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(body, self.session, self.user, 1)
        self.assertIsNone(result)

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query(Contact).filter().first.return_value = contact
        result = await remove_contact(1, self.user, self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query(Contact).filter().first.return_value = None
        result = await remove_contact(1, self.user, self.session)
        self.assertIsNone(result)

    async def test_get_birthday_contact(self):
        now = datetime.now()
        contacts = [Contact(birthday=date(year=now.year, month=now.month, day=now.day)),
                    Contact(birthday=date(year=now.year, month=now.month, day=now.day)),
                    Contact(birthday=date(year=now.year, month=now.month, day=now.day))]
        self.session.query(Contact).filter_by().all.return_value = contacts
        result = await get_birthday_contact(self.user, self.session)
        self.assertEqual(result, contacts)

    async def test_get_birthday_contact_not_found(self):
        now = datetime.now()
        contacts = [Contact(birthday=date(year=now.year, month=now.month, day=now.day)),
                    Contact(birthday=date(year=now.year, month=now.month, day=now.day)),
                    Contact(birthday=date(year=now.year, month=now.month, day=now.day))]
        self.session.query(Contact).filter_by().all.return_value = None
        result = await get_birthday_contact(self.user, self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
