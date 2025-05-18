import os, logging
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
from ldap3.core.exceptions import LDAPBindError

class LdapClient:
    def __init__(self):
        host     = os.getenv('LDAP_HOST')
        port     = os.getenv('LDAP_PORT')
        admin_dn = os.getenv('LDAP_ADMIN_DN')
        admin_pw = os.getenv('LDAP_ADMIN_PASSWORD')
        base_dn  = os.getenv('LDAP_BASE_DN')

        for name,val in [('LDAP_HOST',host),('LDAP_PORT',port),
                         ('LDAP_ADMIN_DN',admin_dn),('LDAP_ADMIN_PASSWORD',admin_pw),
                         ('LDAP_BASE_DN',base_dn)]:
            if not val:
                raise RuntimeError(f"{name} is not set")

        # bind
        server = Server(host, port=int(port), get_info=ALL)
        conn = Connection(server, user=admin_dn, password=admin_pw, auto_bind=False)
        if not conn.bind():
            logging.error("LDAP bind failed: %s", conn.result)
            raise LDAPBindError(conn.result)
        logging.info("LDAP bind OK as %s", admin_dn)
        self.conn = conn
        self.base_dn = base_dn

    def list_users(self):
        self.conn.search(self.base_dn, '(objectClass=person)', attributes=['uid','cn'])
        return [(e.uid.value,e.cn.value) for e in self.conn.entries]

    def add_user(self, uid, pwd, cn=None):
        dn = f"uid={uid},ou=users,{self.base_dn}"
        attrs = {'objectClass':['inetOrgPerson','organizationalPerson','person','top'],
                 'uid':uid,'sn':uid,'cn':cn or uid,'userPassword':pwd}
        return self.conn.add(dn,attributes=attrs)

    def delete_user(self, uid):
        dn = f"uid={uid},ou=users,{self.base_dn}"
        return self.conn.delete(dn)