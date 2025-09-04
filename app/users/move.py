from flask import request, jsonify
from ldap3 import BASE, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE

from audit.audit import log_action
from config import get_connection, USER_OU, GROUPS_BASE, GROUP_OWNER_ATTR
from utils import reassign_parent_owners, ensure_owner_membership


def move_user(uid):
    """Move a user from one group to another.

    If the user owns the source group, ownership is reassigned to the
    parent group's owner so that a group owner is always also a member of
    the group.
    """
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
    if not conn.search(oldg, '(objectClass=groupOfUniqueNames)', BASE, attributes=['uniqueMember', GROUP_OWNER_ATTR]):
        conn.unbind()
        return jsonify({'error': 'old group not found'}), 404
    old_entry = conn.entries[0]
    old_members = set(getattr(old_entry, 'uniqueMember', []))
    old_owner = getattr(old_entry, GROUP_OWNER_ATTR, None)
    if user_dn not in old_members:
        conn.unbind()
        return jsonify({'error': 'user not in old group'}), 400
    if not conn.search(newg, '(objectClass=groupOfUniqueNames)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'new group not found'}), 404
    conn.modify(newg, {'uniqueMember': [(MODIFY_ADD, [user_dn])]})
    if conn.result['description'] not in ('success', 'typeOrValueExists'):
        conn.unbind()
        return jsonify({'error': conn.result}), 400
    if len(old_members) == 1:
        conn.unbind()
        return jsonify({'error': 'cannot move user; old group would have no members'}), 400
    changes = {'uniqueMember': [(MODIFY_DELETE, [user_dn])]}
    new_owner_dn = None
    if old_owner and old_owner.value == user_dn:
        new_owner_dn = reassign_parent_owners(conn, oldg, user_dn)
        if not new_owner_dn:
            conn.unbind()
            return jsonify({'error': 'cannot remove owner; no parent owner found'}), 400
    ok = conn.modify(oldg, changes)
    if not ok or conn.result['description'] != 'success':
        conn.unbind()
        return jsonify({'error': conn.result}), 400
    if new_owner_dn:
        if not ensure_owner_membership(conn, oldg, new_owner_dn):
            conn.unbind()
            return jsonify({'error': 'failed to assign new owner'}), 400
    log_action('move_user', uid=uid, from_group=old_group, to_group=new_group)
    conn.unbind()
    return jsonify({'status': 'moved'}), 200
