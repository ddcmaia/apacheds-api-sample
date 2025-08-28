from flask import jsonify
from ldap3 import BASE, MODIFY_ADD, MODIFY_REPLACE

from audit.audit import log_action
from config import get_connection, GROUPS_BASE, USER_OU, GROUP_OWNER_ATTR


def set_group_owner(group, uid):
    group_dn = f'cn={group},{GROUPS_BASE}'
    user_dn = f'uid={uid},{USER_OU}'
    conn = get_connection()
    # Validate user exists
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    # Validate group exists and get members
    if not conn.search(group_dn, '(objectClass=groupOfUniqueNames)', BASE, attributes=['uniqueMember']):
        conn.unbind()
        return jsonify({'error': 'group not found'}), 404
    entry = conn.entries[0]
    members = set(getattr(entry, 'uniqueMember', []))
    changes = {GROUP_OWNER_ATTR: [(MODIFY_REPLACE, [user_dn])]}
    # Ensure owner is member of group
    if user_dn not in members:
        changes['uniqueMember'] = [(MODIFY_ADD, [user_dn])]
    ok = conn.modify(group_dn, changes)
    result = conn.result
    conn.unbind()
    if ok and result['description'] == 'success':
        log_action('set_group_owner', group=group, owner=uid)
        return jsonify({'status': 'owner set'}), 200
    return jsonify({'error': result}), 400
