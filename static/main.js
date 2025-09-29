// For tv.html: polling the latest URL to auto-redirect

async function checkUrl() {
    try {
        const res = await fetch("/current");
        const data = await res.json();
        if (data.latest_url) {
            window.location.href = data.latest_url;
        }
    } catch (err) {
        console.log("Error fetching latest URL:", err);
    }
}

// Check every 2 seconds
setInterval(checkUrl, 2000);
