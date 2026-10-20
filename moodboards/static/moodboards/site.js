document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".moodboard-card").forEach((card) => {
    card.addEventListener("mouseenter", () => card.classList.add("card-hover"));
    card.addEventListener("mouseleave", () => card.classList.remove("card-hover"));
  });
});
