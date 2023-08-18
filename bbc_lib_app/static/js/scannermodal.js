$(function() {
    $('#topNav .nav-link').each(function() {
        var current = '{{ request.get_full_path | urlencode }}'
        if (current == $(this).attr('href')) {
            $(this).parent().addClass('active')
        }
    })
    $('#scanner-link').click(function(){
        uni_modal("QR Scanner", $(this).attr('data_url'))
    })
})


    const args = {
        video: document.getElementById('scanner'),
        mirror: false
    };

    window.URL.createObjectURL = (stream) => {
        args.video.srcObject = stream;
        return stream;
    };

    const scanner = new Instascan.Scanner(args);
    scanner.addListener('scan', function(content) {
        // alert(content);
        $('.modal').modal('hide')
        start_loader()
        setTimeout(() => {
            uni_modal("View Employee Details", "{% url 'process_qr_code_scan' %}/" + content, 'modal-md')
            scanner.stop()
        }, 500)
    });
    $('#uni_modal').on('shown.bs.modal', function() {
        if ($('#scanner').length > 0) {
            scanner.stop()
            Instascan.Camera.getCameras().then(function(cameras) {
                if (cameras.length > 0) {
                    scanner.start(cameras[0]);
                } else {
                    console.error('No cameras found.');
                }
            }).catch(function(e) {
                console.error(e);
            });
        }
    })
    $('#uni_modal').on('hide.bs.modal', function() {
        scanner.stop()
    })