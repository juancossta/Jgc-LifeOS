document.addEventListener("DOMContentLoaded", () => {
  // Toggle sidebar mobile
  const toggleBtn = document.getElementById("sidebar-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => sidebar.classList.toggle("open"));
  }

  // Dark mode — sincroniza nosso atributo customizado com o data-bs-theme do Bootstrap,
  // que é o que realmente controla a cor de inputs, tabelas, paginação, dropdowns, etc.
  const themeToggle = document.getElementById("theme-toggle");
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("lifeos-theme") || "light";
  aplicarTema(savedTheme);

  function aplicarTema(tema) {
    if (tema === "dark") {
      root.setAttribute("data-theme", "dark");
      root.setAttribute("data-bs-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
      root.setAttribute("data-bs-theme", "light");
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const isDark = root.getAttribute("data-theme") === "dark";
      const novoTema = isDark ? "light" : "dark";
      aplicarTema(novoTema);
      localStorage.setItem("lifeos-theme", novoTema);
    });
  }

  // Confirmação de exclusão
  document.querySelectorAll("[data-confirm-delete]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const msg = form.getAttribute("data-confirm-delete") || "Tem certeza que deseja excluir?";
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // Auto-dismiss flash messages
  document.querySelectorAll(".alert-lifeos").forEach((el) => {
    setTimeout(() => el.classList.add("fade-out"), 4000);
  });
});
