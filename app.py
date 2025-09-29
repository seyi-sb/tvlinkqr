from flask import Flask, render_template, request, redirect, url_for, jsonify
import qrcode
import io
import base64
import socket

app = Flask(__name__)

# Store the latest URL (in memory for now)
latest_url = None


def get_local_ip():
    """Get the local IP address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable, just used to select interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


@app.route("/")
def home():
    return redirect(url_for("tv_page"))

@app.route("/current")
def current():
    global latest_url
    url_to_send = latest_url
    latest_url = None
    return jsonify({"latest_url": url_to_send})

@app.route("/tv")
def tv_page():
    """TV page: shows QR code and always show for control page."""
    """ local_ip = get_local_ip()"""
    host = request.host_url
    remote_url = host + "control"

    qr = qrcode.make(remote_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template("tv.html", qr_code=qr_data)

@app.route("/view")
def tv_view():
    """Redirect TV to the latest entered URL once, then clear it."""
    global latest_url
    if latest_url:
        url_to_open = latest_url
        latest_url = None  # clear so next scan is fresh
        return redirect(url_to_open)
    return "No URL set yet. Use your phone to enter one."

@app.route("/control", methods=["GET", "POST"])
def control():
    """Phone control page: enter a URL to set for the TV."""
    global latest_url

    if request.method == "POST":
        new_url = request.form.get("new_url")

        if new_url:
            # Normalize: add http:// if missing
            if not new_url.startswith(("http://", "https://")):
                new_url = "http://" + new_url

            latest_url = new_url

        return redirect(url_for("control"))

    return render_template("control.html", latest_url=latest_url)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
