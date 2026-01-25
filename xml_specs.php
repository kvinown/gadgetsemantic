<?php
header("Content-type: text/xml");
include 'db_connect.php'; // Pastikan file koneksi database Anda benar

$query = "SELECT * FROM tb_specs";
$result = $conn->query($query);

echo "<?xml version='1.0' encoding='UTF-8'?>";
echo "<catalog>";

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo "<gadget id='" . $row["sku"] . "'>";
        echo "<brand>" . $row["brand"] . "</brand>";
        echo "<model>" . $row["model"] . "</model>";
        
        echo "<teknis>";
        echo "<processor>" . $row["processor"] . "</processor>";
        echo "<ram>" . $row["ram_gb"] . "</ram>";
        echo "<storage>" . $row["storage_gb"] . "</storage>";
        echo "<layar>" . $row["screen_size"] . "</layar>";
        
        // --- BAGIAN BARU UNTUK SKENARIO ---
        echo "<refresh_rate>" . $row["refresh_rate_hz"] . "</refresh_rate>";
        echo "<battery>" . $row["battery_mah"] . "</battery>";
        echo "<camera_mp>" . $row["main_camera_mp"] . "</camera_mp>";
        echo "<telephoto>" . $row["has_telephoto"] . "</telephoto>";
        // ----------------------------------
        
        echo "</teknis>";
        echo "</gadget>";
    }
}
echo "</catalog>";
$conn->close();
?>