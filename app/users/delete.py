from flask import jsonify
from ldap3 import BASE, MODIFY_DELETE

from config import get_connection, USER_OU, GROUPS_BASE


def delete_user(uid):
    user_dn = f'uid={uid},{USER_OU}'
    conn = get_connection()
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    conn.search(GROUPS_BASE, f'(uniqueMember={user_dn})', attributes=['uniqueMember', 'owner', 'cn'])
    for entry in conn.entries:
        members = getattr(entry, 'uniqueMember', [])
        owner_dn = getattr(entry, 'owner', None)
        if len(members) == 1:
            conn.unbind()
            return jsonify({'error': f"cannot delete user; group {entry.cn.value} would have no members"}), 400
        changes = {'uniqueMember': [(MODIFY_DELETE, [user_dn])]}
        if owner_dn and owner_dn.value == user_dn:
            changes['owner'] = [(MODIFY_DELETE, [])]
        conn.modify(entry.entry_dn, changes)
        if conn.result['description'] != 'success':
            conn.unbind()
            return jsonify({'error': conn.result}), 400
    ok = conn.delete(user_dn)
    result = conn.result
    conn.unbind()
    if ok and result['description'] == 'success':
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': result}), 400
