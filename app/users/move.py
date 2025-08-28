from flask import request, jsonify
from ldap3 import BASE, MODIFY_ADD, MODIFY_DELETE

from config import get_connection, USER_OU, GROUPS_BASE


def move_user(uid):
    data = request.json or {}
    old_group = data.get('from')
    new_group = data.get('to')
    if not old_group or not new_group:
        return jsonify({'error': 'from and to groups are required'}), 400
    user_dn = f'uid={uid},{USER_OU}'
    oldg = f'cn={old_group},{GROUPS_BASE}'
    newg = f'cn={new_group},{GROUPS_BASE}'
    conn = get_connection()
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    if not conn.search(oldg, '(objectClass=groupOfUniqueNames)', BASE, attributes=['uniqueMember', 'owner']):
        conn.unbind()
        return jsonify({'error': 'old group not found'}), 404
    old_entry = conn.entries[0]
    old_members = set(getattr(old_entry, 'uniqueMember', []))
    old_owner = getattr(old_entry, 'owner', None)
    if not conn.search(newg, '(objectClass=groupOfUniqueNames)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'new group not found'}), 404
    conn.modify(newg, {'uniqueMember': [(MODIFY_ADD, [user_dn])]})
    if conn.result['description'] not in ('success', 'typeOrValueExists'):
        conn.unbind()
        return jsonify({'error': conn.result}), 400
    if user_dn in old_members:
        if len(old_members) == 1:
            conn.unbind()
            return jsonify({'error': 'cannot move user; old group would have no members'}), 400
        changes = {'uniqueMember': [(MODIFY_DELETE, [user_dn])]}
        if old_owner and old_owner.value == user_dn:
            changes['owner'] = [(MODIFY_DELETE, [])]
        ok = conn.modify(oldg, changes)
        if not ok or conn.result['description'] != 'success':
            conn.unbind()
            return jsonify({'error': conn.result}), 400
    conn.unbind()
    return jsonify({'status': 'moved'}), 200
