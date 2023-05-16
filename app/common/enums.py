from enum import Enum


class PermissionKeys(str, Enum):
    is_creatable = 'is_creatable'
    is_updatable = 'is_updatable'


class ColumnPermissions(dict[str, bool], Enum):
    full = {
        PermissionKeys.is_creatable: True,
        PermissionKeys.is_updatable: True
    }
    create_only = {
        PermissionKeys.is_creatable: True,
        PermissionKeys.is_updatable: False
    }
    update_only = {
        PermissionKeys.is_creatable: False,
        PermissionKeys.is_updatable: True
    }
    none = {
        PermissionKeys.is_creatable: False,
        PermissionKeys.is_updatable: False
    }
