from flask import request, jsonify
from ldap3 import BASE

from audit.audit import log_action
from config import get_connection, USER_OU


def create_user():
    data = request.json or {}
    uid = data.get('uid')
    cn = data.get('cn', uid)
    sn = data.get('sn', uid)
    if not uid:
        return jsonify({'error': 'uid is required'}), 400
    user_dn = f'uid={uid},{USER_OU}'
    attrs = {
        'objectClass': ['inetOrgPerson'],
        'sn': sn,
        'cn': cn,
        'uid': uid,
    }
    conn = get_connection()
    if conn.search(user_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'user already exists'}), 400
    ok = conn.add(user_dn, attributes=attrs)
    result = conn.result
    conn.unbind()
    if ok and result['description'] == 'success':
        log_action('create_user', uid=uid)
        return jsonify({'status': 'created', 'dn': user_dn}), 201
    return jsonify({'error': result}), 400
