from ldap3 import Server, Connection, ALL
import os

LDAP_HOST = os.environ.get('LDAP_HOST', 'apacheds')
LDAP_PORT = int(os.environ.get('LDAP_PORT', '10389'))
LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'uid=admin,ou=system')
LDAP_PASSWORD = os.environ.get('LDAP_PASSWORD', 'secret')
BASE_DN = os.environ.get('BASE_DN', 'dc=example,dc=com')
PEOPLE_BASE = f'dc=people,{BASE_DN}'
GROUPS_BASE = f'dc=groups,{BASE_DN}'
USER_OU = f'ou=Matriz,ou=OrgUsers,{PEOPLE_BASE}'
# Disabled users are moved here instead of being deleted
DISABLED_OU = f'ou=Desativados,ou=OrgUsers,{PEOPLE_BASE}'
GROUP_OWNER_ATTR = 'groupOwner'

# Audit log configuration
AUDIT_LOG = os.environ.get('AUDIT_LOG', 'audit.log')
AUDIT_BUCKET = os.environ.get('AUDIT_BUCKET')
ENABLE_AUDIT_BUCKET = os.environ.get('ENABLE_AUDIT_BUCKET', 'false').lower() == 'true'

def get_connection():
    server = Server(LDAP_HOST, port=LDAP_PORT, get_info=ALL)
    return Connection(server, LDAP_BIND_DN, LDAP_PASSWORD, auto_bind=True)
