package org.springframework.samples.petclinic.api;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class HealthCheck {
    @GetMapping(path="/healthy")
    public String HealthCheck()
    {
        return  "System Online";
    }
}