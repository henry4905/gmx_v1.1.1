document.addEventListener("DOMContentLoaded", function () {

    const titles = document.querySelectorAll(".menu-title");

    titles.forEach(title => {
        title.addEventListener("click", function () {

            const submenu = this.nextElementSibling;

            // Փակում է մնացածները
            document.querySelectorAll(".submenu").forEach(menu => {
                if (menu !== submenu) {
                    menu.style.maxHeight = null;
                }
            });

            // Toggle
            if (submenu.style.maxHeight) {
                submenu.style.maxHeight = null;
            } else {
                submenu.style.maxHeight = submenu.scrollHeight + "px";
            }

        });
    });

});





document.addEventListener("DOMContentLoaded", function () {

    const content = document.getElementById("admin-content");

    document.querySelectorAll(".submenu a").forEach(link => {

        link.addEventListener("click", function (e) {
            e.preventDefault();

            const page = this.dataset.page;

            // Active highlight
            document.querySelectorAll(".submenu a").forEach(l => l.classList.remove("active"));
            this.classList.add("active");

            // Fetch content
            fetch(`/adminpanel/${page}/`)
                .then(response => response.text())
                .then(data => {
                    content.innerHTML = data;
                })
                .catch(error => {
                    content.innerHTML = "<h3>Սխալ տեղի ունեցավ</h3>";
                });

        });

    });

});





// ----------------------------------------------
// LOGO փոփոխություն
// ----------------------------------------------

const input = document.getElementById('logoInput');
const preview = document.getElementById('logoPreview');
const form = document.getElementById('logoForm');

input.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        preview.src = event.target.result;
    }
    reader.readAsDataURL(file);

});



