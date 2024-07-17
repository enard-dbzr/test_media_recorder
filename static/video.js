var socket = io();

document.addEventListener("DOMContentLoaded", () => {
    let video = document.getElementById("video1");

    document.getElementById("btn").addEventListener("click", async () => {
        let uuid = crypto.randomUUID();
        socket.emit("init", uuid);
        console.log(uuid);

        let stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
        video.srcObject = stream;

        let recorder = new MediaRecorder(stream, {mimeType: "video/webm"});

        recorder.addEventListener("dataavailable", (data) => {
            socket.emit("frames", uuid, data.data);
        });

        recorder.start(100); // can be edited for lower latency
    });
});
