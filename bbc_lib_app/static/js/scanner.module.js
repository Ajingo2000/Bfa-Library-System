let toggleScan = document.getElementById("scanner-link");

function qrScanner(){

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

  // Initialize the QR code scanner
  const scanner = new Instascan.Scanner({ video: document.getElementById('scanner') });

  // Listen for QR code detection
  scanner.addListener('scan', function(content) {
      // Send the QR code data to a Django endpoint
      fetch('/process_qr_code_scan/', {
          method: 'POST',
          body: JSON.stringify({ data: content }),
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': '{{ csrf_token }}',  // Add the CSRF token here
          }
      })
      .then(response => response.json())
      .then(data => {
          console.log('Response from server:', data);
          // Handle the server response as needed
      })
      .catch(error => {
          console.error('Error:', error);
      });
  });

// Close the scanner when the modal is closed
document.getElementById('close').addEventListener('click', function() {
  scanner.stop();
});

}

toggleScan.addEventListener('click', function() {
  qrScanner();
});



