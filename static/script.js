document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".left-panel");
  const graph = document.querySelector(".right-panel");

  if (form) {
    form.style.opacity = 0;
    setTimeout(() => {
      form.style.transition = "opacity 0.8s ease";
      form.style.opacity = 1;
    }, 200);
  }

  if (graph) {
    graph.style.opacity = 0;
    setTimeout(() => {
      graph.style.transition = "opacity 0.8s ease";
      graph.style.opacity = 1;
    }, 400);
  }
});
