from flask import request, jsonify
from ldap3 import BASE

from config import get_connection, GROUPS_BASE, USER_OU


def create_group():
    data = request.json or {}
    cn = data.get('cn')
    members = data.get('members') or []
    owner = data.get('owner')
    if not cn or not members:
        return jsonify({'error': 'cn and members are required'}), 400
    group_dn = f'cn={cn},{GROUPS_BASE}'
    conn = get_connection()
    valid_members = []
    for m in members:
        if conn.search(m, '(objectClass=*)', BASE, attributes=[]):
            valid_members.append(m)
        else:
            conn.unbind()
            return jsonify({'error': f'member {m} not found'}), 404
    owner_dn = None
    if owner:
        owner_dn = f'uid={owner},{USER_OU}'
        if not conn.search(owner_dn, '(objectClass=*)', BASE, attributes=[]):
            conn.unbind()
            return jsonify({'error': 'owner not found'}), 404
        if owner_dn not in valid_members:
            valid_members.append(owner_dn)
    attrs = {
        'objectClass': ['groupOfUniqueNames'],
        'cn': cn,
        'uniqueMember': valid_members,
    }
    if owner_dn:
        attrs['owner'] = owner_dn
    ok = conn.add(group_dn, attributes=attrs)
    result = conn.result
    conn.unbind()
    if ok and result['description'] == 'success':
        return jsonify({'status': 'created', 'dn': group_dn}), 201
    return jsonify({'error': result}), 400
