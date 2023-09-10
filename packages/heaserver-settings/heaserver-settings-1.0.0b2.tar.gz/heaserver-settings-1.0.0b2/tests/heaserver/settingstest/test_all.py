from .settingsobjecttestcase import SettingsObjectTestCase
from heaserver.service.testcase.mixin import GetOneMixin, GetAllMixin, PostMixin, PutMixin
import logging


class TestGetSettingsObject(SettingsObjectTestCase, GetOneMixin):
    pass


class TestGetAllSettingsObjects(SettingsObjectTestCase, GetAllMixin):
    pass


class TestPostSettingsObject(SettingsObjectTestCase, PostMixin):
    pass


class TestPutSettingsObject(SettingsObjectTestCase, PutMixin):
    pass


class TestDeleteSettingsObject(SettingsObjectTestCase):
    async def test_delete_then_get(self) -> None:
        """Tries to delete a settings object, which should fail."""
        async with self.client.request('DELETE',
                                       (self._href / self.expected_one_id()).path,
                                       headers=self._headers) as resp:
            self.assertEqual(403, resp.status)

