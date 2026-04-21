const sidebar = document.querySelector(".sidebar");
const container = document.querySelector(".admin-container");
const toggle = document.getElementById("sidebarToggle");

toggle.addEventListener("click", () => {

    sidebar.classList.toggle("closed");
    container.classList.toggle("full");

});



