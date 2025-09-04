from flask import jsonify
from ldap3 import BASE

from audit.audit import log_action
from config import get_connection, GROUPS_BASE, USER_OU
from utils import ensure_owner_membership


def set_group_owner(group, uid):
    """Assign a user as the owner of a group.

    The user is added as a member if necessary so that a group's owner
    can never exist outside the group's membership.
    """
    group_dn = f'cn={group},{GROUPS_BASE}'
    user_dn = f'uid={uid},{USER_OU}'
    conn = get_connection()
    # Validate user exists
    if not conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user not found'}), 404
    # Validate group exists
    if not conn.search(group_dn, '(objectClass=groupOfUniqueNames)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'group not found'}), 404
    ok = ensure_owner_membership(conn, group_dn, user_dn)
    result = conn.result
    if ok and result['description'] == 'success':
        log_action('set_group_owner', group=group, owner=uid)
        conn.unbind()
        return jsonify({'status': 'owner set'}), 200
    conn.unbind()
    return jsonify({'error': result}), 400
