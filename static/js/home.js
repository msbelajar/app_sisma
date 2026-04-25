// Mapping hari dan bulan ke Bahasa Indonesia
    const hariIndonesia = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    };

    const bulanIndonesia = {
        'January': 'Januari',
        'February': 'Februari',
        'March': 'Maret',
        'April': 'April',
        'May': 'Mei',
        'June': 'Juni',
        'July': 'Juli',
        'August': 'Agustus',
        'September': 'September',
        'October': 'Oktober',
        'November': 'November',
        'December': 'Desember'
    };

    // Function untuk convert tanggal ke Bahasa Indonesia
    function formatTanggalIndonesia(tanggalStr) {
        const parts = tanggalStr.split(', ');
        if (parts.length !== 3) return tanggalStr;
        
        const hari = parts[0];
        const hariIndo = hariIndonesia[hari] || hari;
        
        const tengahParts = parts[1].split(' ');
        const bulan = tengahParts[1];
        const bulanIndo = bulanIndonesia[bulan] || bulan;
        
        const tanggal = tengahParts[0];
        const tahun = tengahParts[2];
        
        const waktu = parts[2];
        
        return `${hariIndo}, ${tanggal} ${bulanIndo} ${tahun}, ${waktu}`;
    }

    // Apply formatting untuk semua waktu seminar
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('[data-tanggal]').forEach(function(el) {
            const tanggalStr = el.textContent;
            el.textContent = formatTanggalIndonesia(tanggalStr);
        });
    });