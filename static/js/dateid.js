function formatTanggalIndonesia(tanggalStr) {
        const date = new Date(tanggalStr);
        const formatedid = date.toLocaleDateString("id-ID", {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        })
        return formatedid;
}

// Apply formatting untuk semua waktu seminar
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-tanggal]').forEach(function(el) {
        const tanggalStr = el.textContent;
        el.textContent = formatTanggalIndonesia(tanggalStr);
    });
});