/**
 * Deepproteam - Register Page Logic
 * Handles registration form submission and mock API interaction.
 */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById("registerForm");
    
    // Toggle Password Visibility (reusing logic if element exists)
    // Note: Register page might have multiple password fields (password, confirm)
    // For simplicity, we just look for toggle buttons
    const toggleBtns = document.querySelectorAll('.toggle-pass');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.previousElementSibling;
            if (input && input.tagName === 'INPUT') {
                const isPassword = input.getAttribute("type") === "password";
                input.setAttribute("type", isPassword ? "text" : "password");
                
                const icon = btn.querySelector("i");
                if (icon) {
                    icon.classList.toggle("fa-eye");
                    icon.classList.toggle("fa-eye-slash");
                }
            }
        });
    });

    if (registerForm) {
        registerForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const btn = document.getElementById("registerBtn");
            if (!btn) return;

            // UI Feedback
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner"></div>';
            btn.style.opacity = "0.8";

            // Mock API delay
            setTimeout(() => {
                // Mock Success
                // In real app, we would validate and send data to API
                alert("Account created successfully! Redirecting to login...");
                window.location.href = "login.html";
            }, 1000);
        });
    }
});
