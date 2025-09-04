import os
import sys

# Add the app directory to the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ldap3 import Server, Connection, MOCK_SYNC

from config import GROUPS_BASE, USER_OU, GROUP_OWNER_ATTR
from utils import ensure_owner_membership


def test_setting_owner_does_not_add_membership_to_parent():
    server = Server('fake', get_info=None)
    conn = Connection(server, client_strategy=MOCK_SYNC, check_names=False)
    assert conn.bind()

    user_dn = f'uid=user1,{USER_OU}'
    parent_owner_dn = f'uid=owner_parent,{USER_OU}'
    parent_dn = f'cn=parent,{GROUPS_BASE}'
    child_dn = f'cn=child,{GROUPS_BASE}'

    # Mock directory entries
    conn.strategy.add_entry(user_dn, {'objectClass': 'inetOrgPerson', 'sn': 'User', 'cn': 'User'})
    conn.strategy.add_entry(parent_owner_dn, {'objectClass': 'inetOrgPerson', 'sn': 'Owner', 'cn': 'Owner'})
    conn.strategy.add_entry(parent_dn, {
        'objectClass': ['groupOfUniqueNames'],
        'cn': 'parent',
        'uniqueMember': [child_dn],
        GROUP_OWNER_ATTR: parent_owner_dn,
    })
    conn.strategy.add_entry(child_dn, {
        'objectClass': ['groupOfUniqueNames'],
        'cn': 'child',
        'uniqueMember': [],
    })

    assert ensure_owner_membership(conn, child_dn, user_dn)

    # Child group ownership and membership
    conn.search(child_dn, '(objectClass=*)', attributes=['uniqueMember', GROUP_OWNER_ATTR])
    child_entry = conn.entries[0]
    assert user_dn in str(child_entry[GROUP_OWNER_ATTR].value)
    assert any(user_dn in str(m) for m in child_entry.uniqueMember)

    # Parent group remains unchanged
    conn.search(parent_dn, '(objectClass=*)', attributes=['uniqueMember', GROUP_OWNER_ATTR])
    parent_entry = conn.entries[0]
    assert parent_owner_dn in str(parent_entry[GROUP_OWNER_ATTR].value)
    assert all(user_dn not in str(m) for m in parent_entry.uniqueMember)

