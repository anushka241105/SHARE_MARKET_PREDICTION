document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", () => {
      alert("Generating your stock prediction chart...");
    });
  }
});
