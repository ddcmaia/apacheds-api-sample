from ldap3 import Server, Connection, ALL
import os

LDAP_HOST = os.environ.get('LDAP_HOST', 'apacheds')
LDAP_PORT = int(os.environ.get('LDAP_PORT', '10389'))
LDAP_BIND_DN = os.environ.get('LDAP_BIND_DN', 'uid=admin,ou=system')
LDAP_PASSWORD = os.environ.get('LDAP_PASSWORD', 'secret')
BASE_DN = os.environ.get('BASE_DN', 'dc=example,dc=com')
PEOPLE_BASE = f'dc=people,{BASE_DN}'
GROUPS_BASE = f'dc=groups,{BASE_DN}'
USER_OU = f'ou=HeadOffice,ou=GROUP - Users,{PEOPLE_BASE}'

def get_connection():
    server = Server(LDAP_HOST, port=LDAP_PORT, get_info=ALL)
    return Connection(server, LDAP_BIND_DN, LDAP_PASSWORD, auto_bind=True)
