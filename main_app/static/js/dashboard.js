// Client-side filtering for the User Activity Log table on the dashboard.

(function () {
    const FILTER_IDS = ['filterSearch', 'filterStartDate', 'filterEndDate', 'filterStartTime', 'filterEndTime'];

    function value(id) {
        return document.getElementById(id).value;
    }

    function applyFilters() {
        const search = value('filterSearch').toLowerCase();
        const startDate = value('filterStartDate');
        const endDate = value('filterEndDate');
        const startTime = value('filterStartTime');
        const endTime = value('filterEndTime');

        const rows = document.querySelectorAll('#tableBody tr');
        let visibleCount = 0;

        rows.forEach(function (row) {
            const username = row.dataset.username.toLowerCase();
            const date = row.dataset.date;
            const time = row.dataset.time;

            const visible =
                (!search || username.includes(search)) &&
                (!startDate || date >= startDate) &&
                (!endDate || date <= endDate) &&
                (!startTime || time >= startTime) &&
                (!endTime || time <= endTime);

            row.classList.toggle('hidden', !visible);
            if (visible) visibleCount++;
        });

        document.getElementById('noResults').classList.toggle('hidden', visibleCount > 0);
    }

    document.addEventListener('DOMContentLoaded', function () {
        //ask before submitting destructive forms (ex. Remove Ingested Data)
        document.querySelectorAll('form.js-confirm').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!window.confirm(form.dataset.confirm)) event.preventDefault();
            });
        });

        FILTER_IDS.forEach(function (id) {
            const input = document.getElementById(id);
            input.addEventListener(input.type === 'text' ? 'input' : 'change', applyFilters);
        });
    });
})();
