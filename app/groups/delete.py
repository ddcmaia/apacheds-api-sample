from flask import jsonify
from ldap3 import BASE

from config import get_connection, GROUPS_BASE


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
    conn.unbind()
    if ok and result['description'] == 'success':
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'error': result}), 400
