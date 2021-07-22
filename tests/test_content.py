import pytest
from confluence.client import Confluence
from confluence.models.content import ContentType, ContentStatus
from confluence.exceptions.generalerror import ConfluenceError
from confluence.exceptions.valuetoolong import ConfluenceValueTooLong
from envparse import env

confluence_url = env('CONFLUENCE_URL')
username = env('USER_NAME', default='admin')
password = env('PASSWORD')

instance = Confluence(confluence_url, (username, password))

test_space_key = 'TSTCONTENT'


def setup_module():
    instance.create_space(space_key=test_space_key, space_name='Test contents')


def teardown_module():
    instance.delete_space(space_key=test_space_key)


def test_get_page_content():
    """
    Create content, retrieve it and see if it is the same
    """
    # Create page
    title = 'full test page'
    content = 'this is a full piece of test content'
    page = instance.create_content(ContentType.PAGE,
                                   title=title,
                                   space_key=test_space_key,
                                   content=content)
    assert page.title == title
    # Read page
    returned_page = instance.get_content_by_id(content_id=page.id,
                                               expand=['body.storage'])
    assert returned_page.title == title
    assert returned_page.body.storage == content

    instance.delete_content(content_id=page.id,
                            content_status=ContentStatus.CURRENT)


def test_create_page_with_ancestor():
    """
    Create a child page under a parent page
    """
    parent = instance.create_content(ContentType.PAGE,
                                     title='Parent Page',
                                     space_key=test_space_key,
                                     content="I am the parent")

    try:
        child = instance.create_content(ContentType.PAGE,
                                        title='Child Page',
                                        space_key=test_space_key,
                                        content="I am the child",
                                        parent_content_id=parent.id)
        assert child.title == "Child Page"
        children = instance.get_child_pages(parent.id)
        assert len(list(children)) == 1

        instance.delete_content(content_id=child.id,
                                content_status=ContentStatus.CURRENT)
    finally:
        instance.delete_content(content_id=parent.id,
                                content_status=ContentStatus.CURRENT)


def test_update_page_content():
    """
    Update Page content
    """
    # Create page
    title = 'full test page'
    content = 'this is a full piece of test content'
    result = instance.create_content(ContentType.PAGE,
                                     title=title,
                                     space_key=test_space_key,
                                     content=content,
                                     expand=['body.storage', 'version'])
    assert result.body.storage == content

    # Update page
    upd_title = 'update full test page'
    upd_content = 'this is a full piece of UPDATED test content'
    result = instance.update_content(content_id=result.id,
                                     content_type=result.type,
                                     new_version=result.version.number + 1,
                                     new_content=upd_content,
                                     new_title=upd_title)
    assert result.title == upd_title
    assert result.body.storage == upd_content

    # Read updated page
    result = instance.get_content_by_id(content_id=result.id,
                                        expand=['body.storage'])
    assert result.title == upd_title
    assert result.body.storage == upd_content

    instance.delete_content(content_id=result.id,
                            content_status=ContentStatus.CURRENT)


def test_create_page_in_nonexistent_space():
    """
    Fail to create a page in a non-existent space
    """
    with pytest.raises(ConfluenceError):
        instance.create_content(ContentType.PAGE, title='bad page',
                                space_key='N0NE5UCHSPACE',
                                content='nothing')


def test_get_content_no_results():
    """
    Get content which yield no results
    """
    result = list(instance.get_content(ContentType.PAGE,
                                       space_key=test_space_key,
                                       title='nothing to be found'))
    assert len(result) == 0


def test_get_content_results():
    """
    test get_content with multiple results
    """
    nr_results = 10
    for i in range(nr_results):
        instance.create_content(ContentType.PAGE, title=str(i),
                                space_key=test_space_key, content=str(i))

    pages = list(instance.get_content(ContentType.PAGE,
                                      space_key=test_space_key,
                                      expand=['version']))
    # Results include "space home" hence the + 1
    assert len(pages) == nr_results + 1

    for page in pages[1:]:
        instance.delete_content(content_id=page.id,
                                content_status=ContentStatus.CURRENT)


def test_create_duplicate_page():
    """
    Fail to create a duplicate page
    """
    page = instance.create_content(ContentType.PAGE, title='Duplicate Page',
                                   space_key=test_space_key,
                                   content='some content')

    with pytest.raises(ConfluenceError):
        instance.create_content(ContentType.PAGE, title='Duplicate Page',
                                space_key=test_space_key,
                                content='some content')

    instance.delete_content(content_id=page.id,
                            content_status=ContentStatus.CURRENT)
