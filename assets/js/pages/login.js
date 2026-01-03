document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("togglePass");
  const passInput = document.getElementById("password");
  const loginForm = document.getElementById("loginForm");
  const emailInput = document.getElementById("email");
  const btn = document.getElementById("loginBtn");

  if (toggleBtn && passInput) {
    toggleBtn.addEventListener("click", () => {
      const isPassword = passInput.getAttribute("type") === "password";
      passInput.setAttribute("type", isPassword ? "text" : "password");
      const icon = toggleBtn.querySelector("i");
      if (icon) {
        icon.classList.toggle("fa-eye");
        icon.classList.toggle("fa-eye-slash");
      }
    });
  }

  function createToken(role, email) {
    const header = { alg: "none", typ: "JWT" };
    const exp = Math.floor((Date.now() + 60 * 60 * 1000) / 1000);
    const payload = { exp, role, email };
    const token =
      btoa(JSON.stringify(header)) +
      "." +
      btoa(JSON.stringify(payload)) +
      ".signature";
    return token;
  }

  function createRefreshToken(role, email) {
    const header = { alg: "none", typ: "JWT" };
    const exp = Math.floor((Date.now() + 7 * 24 * 60 * 60 * 1000) / 1000);
    const payload = { exp, role, email };
    const token =
      btoa(JSON.stringify(header)) +
      "." +
      btoa(JSON.stringify(payload)) +
      ".signature";
    return token;
  }

  if (loginForm && emailInput && passInput && btn) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = emailInput.value.trim().toLowerCase();
      const password = passInput.value.trim();
      const originalContent = btn.innerHTML;

      if (!email || !password) {
        alert("Please enter email and password.");
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div>';
      btn.style.opacity = "0.8";

      setTimeout(() => {
        let role = "client";
        if (email === "admin@pro.com" || email.includes("admin")) role = "admin";
        else if (email.includes("dealer")) role = "dealer";

        const access = createToken(role, email);
        const refresh = createRefreshToken(role, email);

        localStorage.setItem("access_token", access);
        localStorage.setItem("refresh_token", refresh);

        let redirect = "client/shop.html";
        if (role === "admin") redirect = "admin/dashboard-admin.html";
        else if (role === "dealer") redirect = "dealer/dashboard.html";

        window.location.href = redirect;
      }, 500);

      setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = originalContent;
        btn.style.opacity = "1";
      }, 600);
    });
  }
});
