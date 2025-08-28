from ldap3 import SUBTREE

from config import GROUPS_BASE, GROUP_OWNER_ATTR


def find_parent_owner(conn, group_dn):
    """Return tuple (parent_dn, owner_dn) for the group if a parent exists."""
    if conn.search(
        GROUPS_BASE,
        f'(uniqueMember={group_dn})',
        SUBTREE,
        attributes=[GROUP_OWNER_ATTR],
    ):
        parent = conn.entries[0]
        owner_attr = getattr(parent, GROUP_OWNER_ATTR, None)
        owner_dn = owner_attr.value if owner_attr else None
        return parent.entry_dn, owner_dn
    return None, None
