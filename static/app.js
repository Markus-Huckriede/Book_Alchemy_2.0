async function registerServiceWorker() {
    if ("serviceWorker" in navigator) {
        try {
            await navigator.serviceWorker.register("/service-worker.js");
        } catch (error) {
            console.info("Service Worker konnte nicht registriert werden.", error);
        }
    }
}

function setupIsbnScanner() {
    const scanButton = document.querySelector("[data-scan-isbn]");
    const input = document.querySelector("#lookup-query");
    const panel = document.querySelector("[data-scanner-panel]");
    const video = document.querySelector("[data-scanner-video]");
    const status = document.querySelector("[data-scanner-status]");

    if (!scanButton || !input || !panel || !video || !status) {
        return;
    }

    let stream;
    let scanning = false;

    const stopScanner = () => {
        scanning = false;
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
        }
        panel.hidden = true;
        scanButton.textContent = "ISBN scannen";
    };

    scanButton.addEventListener("click", async () => {
        if (scanning) {
            stopScanner();
            return;
        }

        if (!("BarcodeDetector" in window)) {
            status.textContent = "Dein Browser unterstützt den Scanner nicht. Bitte gib die ISBN manuell ein.";
            panel.hidden = false;
            return;
        }

        try {
            const detector = new BarcodeDetector({ formats: ["ean_13", "ean_8", "upc_a", "upc_e"] });
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" },
                audio: false,
            });
            video.srcObject = stream;
            await video.play();

            scanning = true;
            panel.hidden = false;
            scanButton.textContent = "Scanner stoppen";
            status.textContent = "Halte den Barcode gut sichtbar vor die Kamera.";

            const scanFrame = async () => {
                if (!scanning) {
                    return;
                }

                const codes = await detector.detect(video);
                if (codes.length > 0) {
                    input.value = codes[0].rawValue;
                    status.textContent = "ISBN erkannt.";
                    stopScanner();
                    input.focus();
                    return;
                }

                requestAnimationFrame(scanFrame);
            };

            requestAnimationFrame(scanFrame);
        } catch (error) {
            status.textContent = "Kamera konnte nicht gestartet werden. Bitte gib die ISBN manuell ein.";
            panel.hidden = false;
            scanning = false;
        }
    });
}

registerServiceWorker();
setupIsbnScanner();
