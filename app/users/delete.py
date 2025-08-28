from flask import jsonify
from ldap3 import BASE, MODIFY_DELETE, MODIFY_REPLACE

from audit.audit import log_action
from config import get_connection, USER_OU, GROUPS_BASE, GROUP_OWNER_ATTR
from utils import find_parent_owner


def delete_user(uid):
    user_dn = f'uid={uid},{USER_OU}'
    conn = get_connection()
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    conn.search(GROUPS_BASE, f'(uniqueMember={user_dn})', attributes=['uniqueMember', GROUP_OWNER_ATTR, 'cn'])
    for entry in conn.entries:
        members = getattr(entry, 'uniqueMember', [])
        owner_dn = getattr(entry, GROUP_OWNER_ATTR, None)
        if len(members) == 1:
            conn.unbind()
            return jsonify({'error': f"cannot delete user; group {entry.cn.value} would have no members"}), 400
        changes = {'uniqueMember': [(MODIFY_DELETE, [user_dn])]}
        if owner_dn and owner_dn.value == user_dn:
            parent_dn, parent_owner = find_parent_owner(conn, entry.entry_dn)
            if parent_owner:
                changes[GROUP_OWNER_ATTR] = [(MODIFY_REPLACE, [parent_owner])]
            else:
                conn.unbind()
                return jsonify({'error': f"cannot delete user; group {entry.cn.value} would have no owner"}), 400
        conn.modify(entry.entry_dn, changes)
        if conn.result['description'] != 'success':
            conn.unbind()
            return jsonify({'error': conn.result}), 400
    ok = conn.delete(user_dn)
    result = conn.result
    if ok and result['description'] == 'success':
        log_action('delete_user', uid=uid)
    conn.unbind()
    if ok and result['description'] == 'success':
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': result}), 400
