"""Constants and object templates for the Google Drive API."""

SHARED_DRIVE = {
    "capabilities": {
        "canAddChildren": True,
        "canChangeCopyRequiresWriterPermissionRestriction": True,
        "canChangeDomainUsersOnlyRestriction": True,
        "canChangeDriveBackground": True,
        "canChangeDriveMembersOnlyRestriction": True,
        "canComment": True,
        "canCopy": True,
        "canDeleteChildren": True,
        "canDeleteDrive": True,
        "canDownload": True,
        "canEdit": True,
        "canListChildren": True,
        "canManageMembers": True,
        "canReadRevisions": True,
        "canRename": True,
        "canRenameDrive": True,
        "canResetDriveRestrictions": True,
        "canShare": True,
        "canTrashChildren": True,
    },
    "hidden": True,
    "restrictions": {
        "adminManagedRestrictions": True,
        "copyRequiresWriterPermission": True,
        "domainUsersOnly": True,
        "driveMembersOnly": True,
    },
}
