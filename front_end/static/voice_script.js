// voice_script.js

const micBtn = document.getElementById("micBtn");
let recorder;
let chunks = [];

micBtn.addEventListener("click", async () => {
    if (micBtn.innerText === "🎤 Speak") {
        startRecording();
    } else {
        stopRecording();
    }
});

async function startRecording() {
    try {
        // Ask for microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);

        chunks = [];
        recorder.ondataavailable = (e) => chunks.push(e.data);

        recorder.onstop = async () => {
            const blob = new Blob(chunks, { type: "audio/webm" });
            const formData = new FormData();
            formData.append("audio", blob, "audio.webm");

            // Updated URL with query params for session_id & user_id
            const url = `http://127.0.0.1:8000/api/chat/audio?session_id=12345&user_id=ishrat`;

            try {
                let res = await fetch(url, {
                    method: "POST",s
                    body: formData
                });

                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

                const data = await res.json();
                document.getElementById("bot").innerText = data.Message || "No response";

            } catch (err) {
                console.error("Bot Error:", err);
                document.getElementById("bot").innerText = "Error contacting bot";
            }
        };

        recorder.start();
        micBtn.innerText = "⏹ Stop";
    } catch (err) {
        console.error("Mic Error:", err);
        alert("Microphone access denied or unavailable");
    }
}

function stopRecording() {
    if (recorder && recorder.state !== "inactive") {
        recorder.stop();
    }
    micBtn.innerText = "🎤 Speak";
}
