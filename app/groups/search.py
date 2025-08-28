from flask import request, jsonify

from config import get_connection, GROUPS_BASE, GROUP_OWNER_ATTR
from utils import find_parent_owner


def search_groups():
    query = request.args.get('q', '(objectClass=groupOfUniqueNames)')
    conn = get_connection()
    if not conn.search(GROUPS_BASE, query, attributes=['cn', 'uniqueMember', GROUP_OWNER_ATTR]):
        result = conn.result
        conn.unbind()
        return jsonify({'error': result}), 400
    results = []
    for entry in conn.entries:
        members_attr = getattr(entry, 'uniqueMember', None)
        members = members_attr.values if members_attr else []
        owner_attr = getattr(entry, GROUP_OWNER_ATTR, None)
        owner = owner_attr.value if owner_attr else None
        parent_dn, parent_owner = find_parent_owner(conn, entry.entry_dn)
        parent = None
        if parent_dn:
            parent = {'dn': parent_dn, 'owner': parent_owner}
        results.append(
            {
                'dn': entry.entry_dn,
                'cn': entry.cn.value,
                'members': members,
                'owner': owner,
                'parent': parent,
            }
        )
    conn.unbind()
    return jsonify(results)
