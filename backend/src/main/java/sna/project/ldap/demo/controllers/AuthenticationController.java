package sna.project.ldap.demo.controllers;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class AuthenticationController {

    @GetMapping("/secgreetings")
    public String getGreeting(Model model) {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();

        System.out.println("Username from SecurityContext: " + username);
        model.addAttribute("name", username);
        return "authenticated";
    }

    @GetMapping("/login")
    public String showLoginForm() {
        return "login";
    }

}
