 document.addEventListener('DOMContentLoaded', function() {
            flatpickr('#id_date_reserved', {
                enableTime: true,
                dateFormat: 'Y-m-d H:i',
                altInput: true,
                altFormat: 'Y-m-d H:i',
                time_24hr: true,
                minDate: "today",
                theme: 'dark',
                "locale": "ru"
                });
            });