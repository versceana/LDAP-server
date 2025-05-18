package sna.project.ldap.demo.dto;

public class UserDto {
    public String getUid() {
        return uid;
    }

    public String getCn() {
        return cn;
    }

    public String getSn() {
        return sn;
    }

    public String getPassword() {
        return password;
    }

    String uid;
    String cn;
    String sn;
    String password;
}
