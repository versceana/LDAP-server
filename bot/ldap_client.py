from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import logging
import os

class LdapClient:
    def __init__(self):
        host = os.getenv('LDAP_HOST')
        port = os.getenv('LDAP_PORT')
        admin_dn = os.getenv('LDAP_ADMIN_DN')
        admin_pw = os.getenv('LDAP_ADMIN_PASSWORD')
        self.base_dn = os.getenv('LDAP_BASE_DN')

        server = Server(host, port=int(port), get_info=ALL)
        self.conn = Connection(server, admin_dn, admin_pw, auto_bind=True)
        logging.info('Connected to LDAP')

    def list_users(self):
        self.conn.search(self.base_dn, '(objectClass=person)', attributes=['cn','uid'])
        return [(e.uid.value, e.cn.value) for e in self.conn.entries]

    def add_user(self, uid, password, cn=None):
        dn = f'uid={uid},ou=users,{self.base_dn}'
        attrs = {
            'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
            'uid': uid,
            'sn': uid,
            'cn': cn or uid,
            'userPassword': password
        }
        result = self.conn.add(dn, attributes=attrs)
        return result

    def delete_user(self, uid):
        dn = f'uid={uid},ou=users,{self.base_dn}'
        return self.conn.delete(dn)