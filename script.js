const API_URL = "http://127.0.0.1:5000/getSensorData";

// Grafik data
const ctx = document.getElementById("sensorChart").getContext("2d");
let chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [], // Waktu data diterima
        datasets: [
            {
                label: "Suhu (°C)",
                data: [],
                borderColor: "#ff5722",
                backgroundColor: "rgba(255, 87, 34, 0.2)",
                fill: true,
            },
            {
                label: "Kelembapan Udara (%)",
                data: [],
                borderColor: "#2196f3",
                backgroundColor: "rgba(33, 150, 243, 0.2)",
                fill: true,
            },
            {
                label: "Kecepatan Angin (m/s)",
                data: [],
                borderColor: "#4caf50",
                backgroundColor: "rgba(76, 175, 80, 0.2)",
                fill: true,
            },
        ],
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: "#2e7d32",
                },
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "Waktu",
                    color: "#2e7d32",
                },
            },
            y: {
                title: {
                    display: true,
                    text: "Nilai",
                    color: "#2e7d32",
                },
                min: 0,
                max: 100,
            },
        },
    },
});

// Data log
let sensorLog = [];

// Fungsi untuk memperbarui dashboard
function updateDashboard(data) {
    document.getElementById("temperature").textContent = `${data.suhu.toFixed(1)} °C`;
    document.getElementById("humidity").textContent = `${data.kelembaban.toFixed(1)} %`;
    document.getElementById("windSpeed").textContent = `${data.kecepatan_angin.toFixed(1)} m/s`;
    document.getElementById("safetystatus").textContent = data.status_keamanan;

    const now = new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    chart.data.labels.push(now);
    chart.data.datasets[0].data.push(data.suhu);
    chart.data.datasets[1].data.push(data.kelembaban);
    chart.data.datasets[2].data.push(data.kecepatan_angin);

    // Batasi jumlah data di grafik (maksimal 10 titik)
    if (chart.data.labels.length > 10) {
        chart.data.labels.shift();
        chart.data.datasets.forEach((dataset) => dataset.data.shift());
    }

    chart.update();

    // Simpan data ke log
    sensorLog.push({
        Waktu: now,
        Suhu: data.suhu,
        Kelembapan_Udara: data.kelembaban,
        Kecepatan_Angin: data.kecepatan_angin,
        Status_Keamanan: data.status_keamanan,
    });
}

// Fungsi untuk mengambil data dari API
async function fetchData() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error("Error fetching data:", error);
        document.getElementById("error").textContent = "Gagal mengambil data dari server.";
    }
}

// Fungsi untuk mendownload log data dalam format Excel
function downloadLogAsExcel() {
    const worksheet = XLSX.utils.json_to_sheet(sensorLog);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Log Data Sensor");
    XLSX.writeFile(workbook, "sensor_log.xlsx");
}

// Tambahkan event listener ke tombol download
document.getElementById("downloadLog").addEventListener("click", downloadLogAsExcel);

// Ambil data dari API setiap 1 menit
setInterval(fetchData, 60000);
fetchData();
