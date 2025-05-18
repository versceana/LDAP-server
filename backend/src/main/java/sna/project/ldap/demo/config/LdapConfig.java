package sna.project.ldap.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.ldap.core.LdapTemplate;
import org.springframework.ldap.core.support.LdapContextSource;

@Configuration
public class LdapConfig {

    @Bean
    public LdapContextSource contextSource() {
        LdapContextSource contextSource = new LdapContextSource();
        contextSource.setUrl("ldap://localhost:1389");
        contextSource.setBase("dc=example,dc=org");
        contextSource.setUserDn("cn=admin,dc=example,dc=org");
        contextSource.setPassword("adminpassword");

        try {
            contextSource.afterPropertiesSet();
            System.out.println("LDAP connection successful!");
        } catch (Exception e) {
            System.err.println("LDAP connection failed: " + e.getMessage());
        }

        return contextSource;
    }

    @Bean
    public LdapTemplate ldapTemplate() {
        return new LdapTemplate(contextSource());
    }
}