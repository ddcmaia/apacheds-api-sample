from flask import request, jsonify
from ldap3 import BASE, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE

from audit.audit import log_action
from config import get_connection, GROUPS_BASE, USER_OU, GROUP_OWNER_ATTR
from utils import find_parent_owner


def remove_user_from_group(group, uid):
    delete_empty = request.args.get('delete_empty_group', 'false').lower() == 'true'
    user_dn = f'uid={uid},{USER_OU}'
    group_dn = f'cn={group},{GROUPS_BASE}'
    conn = get_connection()
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    if not conn.search(group_dn, '(objectClass=*)', BASE, attributes=['uniqueMember', GROUP_OWNER_ATTR]):
        conn.unbind()
        return jsonify({'error': 'group not found'}), 404
    entry = conn.entries[0]
    members = set(getattr(entry, 'uniqueMember', []))
    owner_dn = getattr(entry, GROUP_OWNER_ATTR, None)
    if user_dn not in members:
        conn.unbind()
        return jsonify({'error': 'user not in group'}), 400
    if len(members) == 1:
        if delete_empty:
            parent_dn, _ = find_parent_owner(conn, group_dn)
            ok = conn.delete(group_dn)
            result = conn.result
            if ok and result['description'] == 'success':
                if parent_dn:
                    conn.modify(parent_dn, {'uniqueMember': [(MODIFY_DELETE, [group_dn])]})
                log_action('delete_group', cn=group)
                conn.unbind()
                return jsonify({'status': 'group deleted'}), 200
            conn.unbind()
            return jsonify({'error': result}), 400
        conn.unbind()
        return jsonify({'error': 'cannot remove last member from group'}), 400
    changes = {'uniqueMember': [(MODIFY_DELETE, [user_dn])]}
    if owner_dn and owner_dn.value == user_dn:
        parent_dn, parent_owner = find_parent_owner(conn, group_dn)
        if parent_owner:
            changes[GROUP_OWNER_ATTR] = [(MODIFY_REPLACE, [parent_owner])]
            # move removed owner to parent group if necessary
            if parent_dn and conn.search(parent_dn, '(objectClass=*)', BASE, attributes=['uniqueMember']):
                parent_members = set(getattr(conn.entries[0], 'uniqueMember', []))
                if user_dn not in parent_members:
                    conn.modify(parent_dn, {'uniqueMember': [(MODIFY_ADD, [user_dn])]})
            if parent_dn:
                parent_cn = parent_dn.split(',', 1)[0][3:]
                log_action('move_user_to_parent_group', uid=uid, from_group=group, to_group=parent_cn)
        else:
            conn.unbind()
            return jsonify({'error': 'cannot remove owner; no parent owner found'}), 400
    ok = conn.modify(group_dn, changes)
    result = conn.result
    if ok and result['description'] == 'success':
        log_action('remove_user_from_group', group=group, uid=uid)
    conn.unbind()
    if ok and result['description'] == 'success':
        return jsonify({'status': 'removed'}), 200
    return jsonify({'error': result}), 400
