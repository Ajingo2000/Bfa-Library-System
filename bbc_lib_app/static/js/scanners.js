let toggleScan = document.getElementById("scanner-link");

function qrScanner(){

// Initialize the QR code scanner
const scanner = new Instascan.Scanner({ video: document.getElementById('scanner') });

// Listen for QR code detection
scanner.addListener('scan', function(content) {
    // Send the QR code data to a Django endpoint
    window.location.href = content;
});

// Start scanning
Instascan.Camera.getCameras().then(function(cameras) {
    if (cameras.length > 0) {
        scanner.start(cameras[0]);
    } else {
        console.error('No cameras found.');
    }
}).catch(function(e) {
    console.error('Error:', e);
});

  

// Close the scanner when the modal is closed
document.getElementById('close').addEventListener('click', function() {
  scanner.stop();
});

}

toggleScan.addEventListener('click', function() {
  qrScanner();
});



