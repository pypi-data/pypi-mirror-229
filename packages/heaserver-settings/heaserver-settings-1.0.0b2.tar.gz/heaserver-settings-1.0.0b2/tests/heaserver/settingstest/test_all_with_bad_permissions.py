from .settingsobjectpermissionstestcase import SettingsObjectPermissionsTestCase
from heaserver.service.testcase.mixin import PermissionsPostMixin, PermissionsPutMixin, PermissionsGetOneMixin, \
    PermissionsGetAllMixin, PermissionsDeleteMixin


class TestPostSettingsObjectWithBadPermissions(SettingsObjectPermissionsTestCase, PermissionsPostMixin):
    """A test case class for testing POST requests with bad permissions."""
    pass


class TestPutSettingsObjectWithBadPermissions(SettingsObjectPermissionsTestCase, PermissionsPutMixin):
    """A test case class for testing PUT requests with bad permissions."""
    pass


class TestGetOneSettingsObjectWithBadPermissions(SettingsObjectPermissionsTestCase, PermissionsGetOneMixin):
    """A test case class for testing GET one requests with bad permissions."""
    async def test_get_content_bad_permissions(self) -> None:
        self.skipTest('GET content not defined')

    async def test_get_content_bad_permissions_status(self) -> None:
        self.skipTest('GET content not defined')


class TestGetAllSettingsObjectsWithBadPermissions(SettingsObjectPermissionsTestCase, PermissionsGetAllMixin):
    """A test case class for testing GET all requests with bad permissions."""
    pass


class TestDeleteComponentsWithBadPermissions(SettingsObjectPermissionsTestCase, PermissionsDeleteMixin):
    """A test case class for testing DELETE requests with bad permissions."""
    pass
