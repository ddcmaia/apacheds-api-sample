from flask import request, jsonify
from ldap3 import BASE

from config import get_connection, GROUPS_BASE


def search_groups():
    query = request.args.get('q', '(objectClass=groupOfUniqueNames)')
    conn = get_connection()
    if not conn.search(GROUPS_BASE, query, attributes=['cn', 'uniqueMember', 'owner']):
        result = conn.result
        conn.unbind()
        return jsonify({'error': result}), 400
    results = []
    for entry in conn.entries:
        members_attr = getattr(entry, 'uniqueMember', None)
        members = members_attr.values if members_attr else []
        owner_attr = getattr(entry, 'owner', None)
        owner = owner_attr.value if owner_attr else None
        results.append({
            'dn': entry.entry_dn,
            'cn': entry.cn.value,
            'members': members,
            'owner': owner,
        })
    conn.unbind()
    return jsonify(results)
