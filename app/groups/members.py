from flask import request, jsonify
from ldap3 import BASE, MODIFY_DELETE

from config import get_connection, GROUPS_BASE, USER_OU


def remove_user_from_group(group, uid):
    delete_empty = request.args.get('delete_empty_group', 'false').lower() == 'true'
    user_dn = f'uid={uid},{USER_OU}'
    group_dn = f'cn={group},{GROUPS_BASE}'
    conn = get_connection()
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    if not conn.search(group_dn, '(objectClass=*)', BASE, attributes=['uniqueMember', 'owner']):
        conn.unbind()
        return jsonify({'error': 'group not found'}), 404
    entry = conn.entries[0]
    members = set(getattr(entry, 'uniqueMember', []))
    owner_dn = getattr(entry, 'owner', None)
    if user_dn not in members:
        conn.unbind()
        return jsonify({'error': 'user not in group'}), 400
    if len(members) == 1:
        if delete_empty:
            ok = conn.delete(group_dn)
            result = conn.result
            conn.unbind()
            if ok and result['description'] == 'success':
                return jsonify({'status': 'group deleted'}), 200
            return jsonify({'error': result}), 400
        conn.unbind()
        return jsonify({'error': 'cannot remove last member from group'}), 400
    changes = {'uniqueMember': [(MODIFY_DELETE, [user_dn])]}
    if owner_dn and owner_dn.value == user_dn:
        changes['owner'] = [(MODIFY_DELETE, [])]
    ok = conn.modify(group_dn, changes)
    result = conn.result
    conn.unbind()
    if ok and result['description'] == 'success':
        return jsonify({'status': 'removed'}), 200
    return jsonify({'error': result}), 400
