document.addEventListener("DOMContentLoaded", function () {

    const burger = document.getElementById("nav-toggle");
    const menu = document.querySelector(".header-center");
    const burgerLines = burger.querySelectorAll("span");

    // Toggle menu
    burger.addEventListener("click", function () {
        menu.classList.toggle("active");
        burger.classList.toggle("active");
    });

    // Close menu when clicking on nav item (mobile UX)
    document.querySelectorAll("#main-nav a").forEach(link => {
        link.addEventListener("click", () => {
            if (window.innerWidth <= 900) {
                menu.classList.remove("active");
                burger.classList.remove("active");
            }
        });
    });

});