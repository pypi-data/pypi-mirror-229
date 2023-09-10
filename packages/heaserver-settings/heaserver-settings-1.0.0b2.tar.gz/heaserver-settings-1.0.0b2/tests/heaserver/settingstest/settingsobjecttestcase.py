"""
Creates a test case class for use with the unittest library that is build into Python.
"""

from heaserver.service.testcase.microservicetestcase import get_test_case_cls_default
from heaserver.settings import service
from heaobject.user import NONE_USER, TEST_USER
from heaobject.root import Permission
from heaobject.registry import Collection
from heaobject.keychain import Credentials
from heaobject.person import Person
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    service.MONGODB_SETTINGS_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'display_name': 'Credentials',
        'name': 'heasettings|credentials',
        'owner': NONE_USER,
        'type': 'heaobject.settings.SettingsObject',
        'user': TEST_USER,
        'shares': [{
            'invite': None,
            'type': 'heaobject.root.ShareImpl',
            'user': TEST_USER,
            'permissions': [Permission.VIEWER.name, Permission.EDITOR.name, Permission.CHECK_DYNAMIC.name]
        }],
        'actual_object_type_name': Collection.get_type_name(),
        'actual_object_uri': f'collections/{Credentials.get_type_name()}',
        'actual_object_id': Credentials.get_type_name()
    },
    {
        'id': '0123456789ab0123456789ab',
        'display_name': 'Profile',
        'invites': [],
        'modified': None,
        'name': 'heasettings|profile',
        'owner': NONE_USER,
        'type': 'heaobject.settings.SettingsObject',
        'user': TEST_USER,
        'shares': [{
            'invite': None,
            'type': 'heaobject.root.ShareImpl',
            'user': TEST_USER,
            'permissions': [Permission.VIEWER.name, Permission.EDITOR.name, Permission.CHECK_DYNAMIC.name]
        }],
        'actual_object_type_name': Person.get_type_name(),
        'actual_object_uri': 'people/me',
        'actual_object_id': 'me'
    }]}

SettingsObjectTestCase = get_test_case_cls_default(coll=service.MONGODB_SETTINGS_COLLECTION,
                                              href='http://localhost:8080/settings',
                                              wstl_package=service.__package__,
                                              fixtures=db_store,
                                              get_actions=[
                                                  Action(name='heaserver-settings-settings-object-get-properties',
                                                         rel=['hea-properties']),
                                                  Action(name='heaserver-settings-settings-object-get-open-choices',
                                                         rel=['hea-opener-choices'],
                                                         url='http://localhost:8080/settings/{id}/opener'),
                                                  Action(name='heaserver-settings-settings-object-get-self',
                                                         rel=['self'],
                                                         url='http://localhost:8080/settings/{id}'),
                                                  Action(name='heaserver-settings-settings-object-get-actual',
                                                         rel=['hea-actual'],
                                                         url='http://localhost:8080/{+actual_object_uri}')
                                              ],
                                              get_all_actions=[
                                                  Action(name='heaserver-settings-settings-object-get-properties',
                                                         rel=['hea-properties']),
                                                  Action(name='heaserver-settings-settings-object-get-open-choices',
                                                         rel=['hea-opener-choices'],
                                                         url='http://localhost:8080/settings/{id}/opener'),
                                                  Action(name='heaserver-settings-settings-object-get-self',
                                                         rel=['self'],
                                                         url='http://localhost:8080/settings/{id}'),
                                                  Action(name='heaserver-settings-settings-object-get-actual',
                                                         rel=['hea-actual'],
                                                         url='http://localhost:8080/{+actual_object_uri}')],
                                              sub=TEST_USER)
