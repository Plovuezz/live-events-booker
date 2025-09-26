document.addEventListener("DOMContentLoaded", function() {
  const navbar = document.querySelector(".navbar");

  function checkScroll() {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  }

  checkScroll();
  window.addEventListener("scroll", checkScroll);
});