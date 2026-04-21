document.addEventListener('DOMContentLoaded', function () {
    // Find all tree rows
    const treeRows = document.querySelectorAll('.model-category tr');

    treeRows.forEach(row => {
        const level = parseInt(row.dataset.level || 0);
        if (level > 0) {
            row.style.display = 'none'; // hide subcategories initially
        }

        const toggleCell = row.querySelector('th, td');
        if (toggleCell) {
            const expandBtn = document.createElement('span');
            expandBtn.textContent = '+';
            expandBtn.style.cursor = 'pointer';
            expandBtn.style.marginRight = '5px';
            toggleCell.prepend(expandBtn);

            expandBtn.addEventListener('click', () => {
                const rowLevel = parseInt(row.dataset.level);
                let showing = expandBtn.textContent === '-';
                expandBtn.textContent = showing ? '+' : '-';

                let nextRow = row.nextElementSibling;
                while (nextRow) {
                    const nextLevel = parseInt(nextRow.dataset.level || 0);
                    if (nextLevel <= rowLevel) break;

                    if (!showing && nextLevel === rowLevel + 1) {
                        nextRow.style.display = '';
                    } else if (showing) {
                        nextRow.style.display = 'none';
                        // recursively collapse child subcategories
                        const childBtn = nextRow.querySelector('span');
                        if (childBtn) childBtn.textContent = '+';
                    }
                    nextRow = nextRow.nextElementSibling;
                }
            });
        }
    });

    // Simple drag & drop
    treeRows.forEach(row => {
        row.draggable = true;
        row.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', row.dataset.pk);
            row.classList.add('dragging');
        });
        row.addEventListener('dragend', e => {
            row.classList.remove('dragging');
        });

        row.addEventListener('dragover', e => {
            e.preventDefault();
        });

        row.addEventListener('drop', e => {
            e.preventDefault();
            const draggedPk = e.dataTransfer.getData('text/plain');
            const targetPk = row.dataset.pk;

            // Simple visual reorder
            const draggedRow = document.querySelector(`tr[data-pk='${draggedPk}']`);
            row.parentNode.insertBefore(draggedRow, row.nextSibling);

            // TODO: Ajax call to update order in DB
            console.log(`Moved category ${draggedPk} after ${targetPk}`);
        });
    });
});