from flask import jsonify
from ldap3 import BASE, MODIFY_DELETE

from audit.audit import log_action
from config import get_connection, GROUPS_BASE
from utils import find_parent_owner


def delete_group(group):
    group_dn = f'cn={group},{GROUPS_BASE}'
    conn = get_connection()
    if not conn.search(group_dn, '(objectClass=groupOfUniqueNames)', BASE, attributes=['uniqueMember']):
        conn.unbind()
        return jsonify({'error': 'group not found'}), 404
    members = getattr(conn.entries[0], 'uniqueMember', [])
    if members:
        conn.unbind()
        return jsonify({'error': 'group is not empty'}), 400
    ok = conn.delete(group_dn)
    result = conn.result
    if ok and result['description'] == 'success':
        parent_dn, _ = find_parent_owner(conn, group_dn)
        if parent_dn:
            conn.modify(parent_dn, {'uniqueMember': [(MODIFY_DELETE, [group_dn])]})
        log_action('delete_group', cn=group)
        conn.unbind()
        return jsonify({'status': 'deleted'}), 200
    conn.unbind()
    return jsonify({'error': result}), 400
