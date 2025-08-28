from flask import request, jsonify
from ldap3 import BASE, MODIFY_ADD

from audit.audit import log_action
from config import get_connection, GROUPS_BASE, USER_OU, GROUP_OWNER_ATTR


def create_group():
    data = request.json or {}
    cn = data.get('cn')
    members = data.get('members') or []
    owner = data.get('owner')
    parent = data.get('parent')
    if not cn or not members or not owner:
        return jsonify({'error': 'cn, members and owner are required'}), 400
    if not (cn.startswith('GU_') or cn.startswith('GG_')):
        return jsonify({'error': 'group name must start with GU_ or GG_'}), 400
    group_dn = f'cn={cn},{GROUPS_BASE}'
    conn = get_connection()
    parent_dn = None
    if cn.startswith('GG_'):
        if not parent or not parent.startswith('GU_'):
            conn.unbind()
            return jsonify({'error': 'GG_ groups require a parent GU_ group'}), 400
        parent_dn = f'cn={parent},{GROUPS_BASE}'
        if not conn.search(parent_dn, '(objectClass=groupOfUniqueNames)', BASE, attributes=['uniqueMember']):
            conn.unbind()
            return jsonify({'error': 'parent group not found'}), 404
    elif parent:
        conn.unbind()
        return jsonify({'error': 'GU_ groups cannot have a parent'}), 400

    valid_members = []
    for m in members:
        if conn.search(m, '(objectClass=*)', BASE, attributes=[]):
            valid_members.append(m)
        else:
            conn.unbind()
            return jsonify({'error': f'member {m} not found'}), 404
    owner_dn = f'uid={owner},{USER_OU}'
    if not conn.search(owner_dn, '(objectClass=*)', BASE, attributes=[]):
        conn.unbind()
        return jsonify({'error': 'owner not found'}), 404
    if owner_dn not in valid_members:
        valid_members.append(owner_dn)
    attrs = {
        'objectClass': ['groupOfUniqueNames', 'groupWithOwner'],
        'cn': cn,
        'uniqueMember': valid_members,
    }
    if owner_dn:
        attrs[GROUP_OWNER_ATTR] = owner_dn
    ok = conn.add(group_dn, attributes=attrs)
    result = conn.result
    if ok and result['description'] == 'success' and parent_dn:
        conn.modify(parent_dn, {'uniqueMember': [(MODIFY_ADD, [group_dn])]})
    conn.unbind()
    if ok and result['description'] == 'success':
        log_action('create_group', cn=cn, parent=parent, owner=owner)
        return jsonify({'status': 'created', 'dn': group_dn}), 201
    return jsonify({'error': result}), 400
