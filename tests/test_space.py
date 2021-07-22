from confluence.client import Confluence
from envparse import env

confluence_url = env('CONFLUENCE_URL')
username = env('USER_NAME', default='admin')
password = env('PASSWORD')

instance = Confluence(confluence_url, (username, password))

test_space_key = 'TSTSPACE'


def test_create_space():
    """
    Create space to confluence url
    """
    space = instance.create_space(space_key=test_space_key,
                                  space_name='Heroes Test')
    assert space.key == test_space_key
    assert space.name == 'Heroes Test'


def test_get_space():
    """
    Get space to confluence url
    """
    space = instance.get_space(space_key=test_space_key)
    assert space.key == test_space_key


def test_update_space():
    """
    Update space to confluence url
    """
    space = instance.update_space(space_key=test_space_key,
                                  new_name='Update Test',
                                  new_description=None)
    assert space.name == 'Update Test'


def test_delete_space():
    """
    Delete space to confluence url
    """
    space = instance.delete_space(space_key=test_space_key)
    assert space is None
