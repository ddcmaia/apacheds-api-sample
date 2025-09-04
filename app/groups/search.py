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
        attrs = entry.entry_attributes_as_dict
        members = attrs.get('uniqueMember', [])
        owner = attrs.get(GROUP_OWNER_ATTR, [None])[0]
        parent_dn, parent_owner = find_parent_owner(conn, entry.entry_dn)
        parent = {'dn': parent_dn, 'owner': parent_owner} if parent_dn else None
        results.append(
            {
                'dn': entry.entry_dn,
                'cn': attrs['cn'][0],
                'members': members,
                'owner': owner,
                'parent': parent,
            }
        )
    conn.unbind()
    return jsonify(results)
