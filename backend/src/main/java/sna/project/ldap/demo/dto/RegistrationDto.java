package sna.project.ldap.demo.dto;


public record RegistrationDto() {
    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    static String username;
    static String password;
}