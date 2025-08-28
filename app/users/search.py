from flask import request, jsonify
from ldap3 import BASE

from config import get_connection, USER_OU


def search_users():
    query = request.args.get('q', '(objectClass=inetOrgPerson)')
    conn = get_connection()
    if not conn.search(USER_OU, query, attributes=['uid', 'cn', 'sn']):
        result = conn.result
        conn.unbind()
        return jsonify({'error': result}), 400
    results = []
    for entry in conn.entries:
        results.append({'dn': entry.entry_dn, 'uid': entry.uid.value, 'cn': entry.cn.value, 'sn': entry.sn.value})
    conn.unbind()
    return jsonify(results)
