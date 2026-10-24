from cone.app import get_root
from cone.ugm import testing
from zope.event import classhandler


# ``admin_group_1`` manages ``managed_group_0`` and ``managed_group_1``, the
# latter is its default group. See ``cone.ugm.testing.localmanager_config``.
local_manager_principals = testing.principals(
    users={
        'manager': {},
        'editor': {},
        'local_manager': {},
        'local_editor': {},
        'managed_user': {},
        'unmanaged_user': {},
    },
    groups={
        'admin_group_1': {},
        'managed_group_0': {},
        'managed_group_1': {},
        'managed_group_2': {},
    },
    membership={
        'admin_group_1': ['local_manager', 'local_editor'],
        'managed_group_1': ['managed_user'],
        'managed_group_2': ['unmanaged_user'],
    },
    roles={
        'manager': ['manager'],
        'editor': ['editor'],
        'local_editor': ['editor'],
    },
)


def local_management_enabled(fn):
    """Decorator for tests running with local management enabled."""

    def wrapper(*a, **kw):
        settings = get_root()['settings']['ugm_general']
        settings.attrs.users_local_management_enabled = 'True'
        try:
            fn(*a, **kw)
        finally:
            settings.invalidate()

    return wrapper


def register_event_handler(testcase, event_class, handler):
    """Register ``handler`` for ``event_class`` and unregister it when
    ``testcase`` is finished."""
    classhandler.handler(event_class, handler)
    testcase.addCleanup(classhandler.registry[event_class].remove, handler)
