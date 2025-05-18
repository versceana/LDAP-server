package sna.project.ldap.demo.controllers;

import org.springframework.ldap.core.DirContextAdapter;
import org.springframework.ldap.core.LdapTemplate;
import org.springframework.ldap.support.LdapNameBuilder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import sna.project.ldap.demo.dto.RegistrationDto;

import javax.naming.Name;

@Controller
@RequestMapping("/api/auth")
public class AuthController {

    private final LdapTemplate ldapTemplate;

    public AuthController(LdapTemplate ldapTemplate) {
        this.ldapTemplate = ldapTemplate;
    }

    @GetMapping("/registration")
    public String showRegistrationForm(Model model) {
        model.addAttribute("user", new RegistrationDto());
        return "registration";
    }

    @PostMapping("/register")
    public String register(@ModelAttribute("user") RegistrationDto registrationDto, Model model) {
        System.out.println("mi try to reg new");
        try {
            registerNewUser(registrationDto.getUsername(), registrationDto.getPassword());
            return "redirect:/login?registered"; // Перенаправляем на страницу логина с параметром
        } catch (Exception e) {
            model.addAttribute("error", "Registration failed: " + e.getMessage());
            return "registration"; // Возвращаем обратно на форму с ошибкой
        }
    }

    private void registerNewUser(String username, String password) {
        try {
            Name dn = LdapNameBuilder.newInstance()
                    .add("ou", "users")
                    .add("cn", username)
                    .build();

            System.out.println("Attempting to create user with DN: " + dn);

            DirContextAdapter context = new DirContextAdapter(dn);

            context.setAttributeValues("objectClass",
                    new String[]{"top", "person", "organizationalPerson", "inetOrgPerson"});
            context.setAttributeValue("cn", username);
            context.setAttributeValue("sn", username);
            context.setAttributeValue("userPassword", password);

            ldapTemplate.bind(context);
            System.out.println("User created successfully");
        } catch (Exception e) {
            System.err.println("Error creating user: " + e.getClass().getName() + ": " + e.getMessage());
            throw e;
        }
    }
}