from ldap3 import BASE, SUBTREE, MODIFY_ADD, MODIFY_REPLACE

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


def ensure_owner_membership(conn, group_dn, owner_dn):
    """Set the group's owner ensuring the owner is also a member."""
    if not conn.search(
        group_dn, "(objectClass=groupOfUniqueNames)", BASE, attributes=["uniqueMember"]
    ):
        return False
    entry = conn.entries[0]
    members = set(getattr(entry, "uniqueMember", []))
    changes = {GROUP_OWNER_ATTR: [(MODIFY_REPLACE, [owner_dn])]}
    if owner_dn not in members:
        changes["uniqueMember"] = [(MODIFY_ADD, [owner_dn])]
    ok = conn.modify(group_dn, changes)
    return ok and conn.result["description"] == "success"


def reassign_parent_owners(conn, group_dn, removed_owner_dn):
    """Cascade ownership changes up the hierarchy when an owner leaves."""
    parent_dn, parent_owner = find_parent_owner(conn, group_dn)
    if not parent_dn:
        return None
    if parent_owner == removed_owner_dn:
        new_owner = reassign_parent_owners(conn, parent_dn, removed_owner_dn)
        if not new_owner:
            return None
    else:
        new_owner = parent_owner
    if not ensure_owner_membership(conn, parent_dn, new_owner):
        return None
    return new_owner
