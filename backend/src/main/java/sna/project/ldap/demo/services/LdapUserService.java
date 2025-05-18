package sna.project.ldap.demo.services;

import org.springframework.ldap.core.DirContextAdapter;
import org.springframework.ldap.core.LdapTemplate;
import org.springframework.ldap.support.LdapNameBuilder;
import org.springframework.stereotype.Service;

import javax.naming.Name;

@Service
public class LdapUserService {

    private final LdapTemplate ldapTemplate;

    public LdapUserService(LdapTemplate ldapTemplate) {
        this.ldapTemplate = ldapTemplate;
    }

    public void addUser(String uid, String cn, String sn, String password) {
        Name dn = buildDn(uid);
        DirContextAdapter context = new DirContextAdapter(dn);
        context.setAttributeValues("objectClass", new String[] { "inetOrgPerson", "organizationalPerson", "person", "top" });
        context.setAttributeValue("cn", cn);
        context.setAttributeValue("sn", sn);
        context.setAttributeValue("uid", uid);
        context.setAttributeValue("userPassword", password);
        ldapTemplate.bind(context);
    }

    private Name buildDn(String uid) {
        return LdapNameBuilder.newInstance("ou=users,dc=example,dc=org")
                .add("uid", uid)
                .build();
    }
}
