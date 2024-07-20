var socket = io();

document.addEventListener("DOMContentLoaded", () => {
    // const canvas = document.getElementById('myChart');

    let video = document.getElementById("video1");
    let startButton = document.getElementById("start-btn");
    let stopButton = document.getElementById("stop-btn");

    let recorder;

    startButton.addEventListener("click", async () => {
        let bpp = [];
        let chart = new CanvasJS.Chart("chartContainer", {
            animationEnabled: true,
	        zoomEnabled: true,
            data: [
                {
                    showInLegend: true,
                    name: "Bytes per packet",
                    toolTipContent: "Bytes per packet: {y}<br/>Actual bitrate: {bps} Kbit/s",
                    color: "#369EAD",
                    type: "line",
                    dataPoints: bpp
                }
            ]
        });

        let bitrate = document.getElementById("bitrate").value;
        let timeslice = document.getElementById("timeslice").value;

        let uuid = Date.now();
        console.log(uuid);

        let stream;

        try {
            stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
            video.srcObject = stream;

            let mimeType = MediaRecorder.isTypeSupported("video/webm") ? "video/webm" : "video/mp4";
            console.log(mimeType);

            socket.emit("init", uuid, mimeType);


            let options = {
                mimeType: mimeType,
                bitsPerSecond: bitrate
            };

            recorder = new MediaRecorder(stream, options);
            let chunkCounter = 0;

            recorder.addEventListener("dataavailable", (data) => {
                try {
                    chunkCounter++
                    bpp.push({
                        x: chunkCounter,
                        y: data.data.size,
                        bps: (data.data.size * 8 / timeslice).toFixed(2)
                    });

                    chart.render();

                    socket.emit("frames", uuid, data.data);
                } catch (err) {
                    alert(err);
                    recorder.stop()
                }
            });

            recorder.addEventListener("stop", () => {
                video.srcObject = null;

                stream.getTracks().forEach(function(track) {
                    track.stop();
                });

                socket.emit("stop", uuid);
            });

            recorder.start(timeslice); // can be edited for lower latency
        } catch (err){
            alert(err);
        }
    });

    stopButton.addEventListener("click", () => {
        recorder.stop();
    });

});
