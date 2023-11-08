const b64toBlob = (b64Data, contentType = '', sliceSize = 512) => {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
        byteArrays.push(byteArray);
    }

    const blob = new Blob(byteArrays, { type: contentType });
    return blob;
}

let constraintObj = {
    audio: { noiseSuppression: true },
    video: false
};
if (navigator.mediaDevices === undefined) {
    navigator.mediaDevices = {};
    navigator.mediaDevices.getUserMedia = function (constraintObj) {
        let getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
        if (!getUserMedia) {
            return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
        }
        return new Promise(function (resolve, reject) {
            getUserMedia.call(navigator, constraintObj, resolve, reject);
        });
    }
} else {
    navigator.mediaDevices.enumerateDevices()
        .then(devices => {
            devices.forEach(device => {
                console.log(device.kind.toUpperCase(), device.label);
                //, device.deviceId
            })
        })
        .catch(err => {
            console.log(err.name, err.message);
        })
}

navigator.mediaDevices.getUserMedia(constraintObj)
    .then(function (mediaStreamObj) {
        //connect the media stream to the first audio element
        let audio = document.getElementById('audio_stream')
        if ("srcObject" in audio) {
            audio.srcObject = mediaStreamObj;
        } else {
            //old version
            audio.src = window.URL.createObjectURL(mediaStreamObj);
        }

        audio.onloadedmetadata = function (ev) {
            //show in the audio element what is being captured by the webcam
            audio.play();
        };

        let toggle = document.getElementById('mic_toggle');
        let mediaRecorder = new MediaRecorder(mediaStreamObj);
        let chunks = [];

        toggle.addEventListener('change', async function () {
            if (this.checked) {
                mediaRecorder.start();
                console.log(mediaRecorder.state);
            }
            else {
                mediaRecorder.stop();
                console.log(mediaRecorder.state);

                document.getElementById("send_btn").style.visibility = "visible";
                $('#mic_toggle_l').attr('style', 'animation: squeeze 150ms ease 1;opacity:0;');
                $('#send_btn').attr('style', 'animation: expand 150ms ease 1');
                await sleep(150)
                document.getElementById("mic_toggle_l").style.visibility = "hidden";
            }
        });

        mediaRecorder.ondataavailable = function (ev) {
            chunks.push(ev.data);
        }
        mediaRecorder.onstop = (ev) => {
            let blob = new Blob(chunks, { 'type': 'audio/mp3;' });
            var reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = function () {
                var base64data = reader.result;
                $('#message').val(base64data);
                document.getElementById("send_btn").click();
                $('#message').val('');
            }
            chunks = [];
        }
    })
    .catch(function (err) {
        console.log(err.name, err.message);
    });