(function () {
  const root = document.documentElement;
  const toggleBtn = document.getElementById("theme-toggle");
  const stored = localStorage.getItem("clinton-tech-theme");

  if (stored) {
    root.setAttribute("data-theme", stored);
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    root.setAttribute("data-theme", "dark");
  }

  function updateIcon() {
    if (toggleBtn) {
      toggleBtn.textContent = root.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";
    }
  }
  updateIcon();

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("clinton-tech-theme", next);
      updateIcon();
    });
  }
})();
