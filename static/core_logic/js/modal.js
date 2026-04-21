function openModal(modalHTML) {
    // Եթե արդեն կա, ջնջում ենք հին modal-ը
    let existing = document.getElementById("customModal");
    if (existing) existing.remove();

    // Ստեղծում նոր modal
    let div = document.createElement("div");
    div.innerHTML = modalHTML;
    document.body.appendChild(div.firstElementChild);
}

function closeModal() {
    let modal = document.getElementById("customModal");
    if (modal) modal.remove();
}
