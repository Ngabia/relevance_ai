import time
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, send_file
import os
import threading

app = Flask(__name__)
qr_image_path = "static/qr_code.png"
status_file = "static/status.txt"
checkmark_path = "static/checkmark.png.webp"  # Ensure checkmark image is in static/

# Ensure 'static' folder exists
if not os.path.exists("static"):
    os.makedirs("static")

# Create status file if not exists
if not os.path.exists(status_file):
    with open(status_file, "w") as f:
        f.write("waiting")

def init_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://web.whatsapp.com")
    print("Please scan the QR code to log in.")

    time.sleep(10)  # Wait for the page to load

    while True:
        try:
            print("Attempting to extract QR code...")
            qr_canvas = driver.find_element("css selector", "canvas")
            qr_canvas.screenshot(qr_image_path)
            print(f"✅ QR Code extracted and saved at {qr_image_path}")

            # Reset status to 'waiting' if QR is extracted
            with open(status_file, "w") as f:
                f.write("waiting")

            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"❌ Error extracting QR code: {e}")

            # Check if user is logged in by finding the "Chats" heading
            try:
                chats_heading = driver.find_element("xpath", "//h1[contains(@class, 'x1qlqyl8') and contains(text(), 'Chats')]")
                if chats_heading:
                    print("✅ WhatsApp Login successful!")
                    with open(status_file, "w") as f:
                        f.write("logged_in")
            except:
                pass  # Continue loop if not found
            break

    return driver

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/qr_code')
def get_qr_code():
    if os.path.exists(qr_image_path):
        return send_file(qr_image_path, mimetype='image/png')
    else:
        return "QR Code not available yet.", 404

@app.route('/status')
def get_status():
    with open(status_file, "r") as f:
        return f.read()

@app.route('/checkmark')
def get_checkmark():
    return send_file(checkmark_path, mimetype='image/png')

def run_flask():
    print("Starting Flask server on http://127.0.0.1:5000/ ...")
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    driver = init_whatsapp()
