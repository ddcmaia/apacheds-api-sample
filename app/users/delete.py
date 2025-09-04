from flask import jsonify
from ldap3 import BASE, MODIFY_DELETE, MODIFY_REPLACE

from audit.audit import log_action
from config import (
    get_connection,
    USER_OU,
    GROUPS_BASE,
    GROUP_OWNER_ATTR,
    # location for disabled users
    DISABLED_OU,
)
from utils import reassign_parent_owners, ensure_owner_membership


def delete_user(uid):
    """Deactivate a user by removing them from groups and disabling the entry.

    The user's accountStatus is set to ``inactive`` and the entry is moved to
    the ``DISABLED_OU`` instead of being deleted so that audit history is
    preserved.
    """

    user_dn = f'uid={uid},{USER_OU}'
    conn = get_connection()
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404

    conn.search(
        GROUPS_BASE,
        f'(|(uniqueMember={user_dn})({GROUP_OWNER_ATTR}={user_dn}))',
        attributes=['uniqueMember', GROUP_OWNER_ATTR, 'cn'],
    )
    for entry in conn.entries:
        members = set(getattr(entry, 'uniqueMember', []))
        owner_attr = getattr(entry, GROUP_OWNER_ATTR, None)
        is_member = user_dn in members
        new_owner_dn = None

        if is_member and len(members) == 1:
            conn.unbind()
            return jsonify(
                {
                    'error': f"cannot deactivate user; group {entry.cn.value} would have no members"
                }
            ), 400

        if owner_attr and owner_attr.value == user_dn:
            new_owner_dn = reassign_parent_owners(conn, entry.entry_dn, user_dn)
            if not new_owner_dn:
                conn.unbind()
                return jsonify(
                    {
                        'error': f"cannot deactivate user; group {entry.cn.value} would have no owner"
                    }
                ), 400

        changes = {}
        if is_member:
            changes['uniqueMember'] = [(MODIFY_DELETE, [user_dn])]

        if changes:
            ok = conn.modify(entry.entry_dn, changes)
            if not ok or conn.result['description'] != 'success':
                conn.unbind()
                return jsonify({'error': conn.result}), 400

        if new_owner_dn:
            if not ensure_owner_membership(conn, entry.entry_dn, new_owner_dn):
                conn.unbind()
                return jsonify({'error': 'failed to assign new owner'}), 400

    # mark account as inactive
    conn.modify(user_dn, {'accountStatus': [(MODIFY_REPLACE, ['inactive'])]})
    if conn.result['description'] != 'success':
        result = conn.result
        conn.unbind()
        return jsonify({'error': result}), 400

    # move entry to disabled OU
    ok = conn.modify_dn(user_dn, f'uid={uid}', new_superior=DISABLED_OU)
    result = conn.result
    if ok and result['description'] == 'success':
        log_action('deactivate_user', uid=uid)
        conn.unbind()
        return jsonify({'status': 'deactivated'}), 200

    conn.unbind()
    return jsonify({'error': result}), 400
