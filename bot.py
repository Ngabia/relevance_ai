import time
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, send_file
import os
import threading

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
qr_image_path = "static/qr_code.png"

# Ensure the 'static' folder exists
if not os.path.exists("static"):
    os.makedirs("static")

def init_whatsapp():
    """Initializes WhatsApp Web and extracts the QR code."""
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Disable sandboxing for headless mode
    options.add_argument("--disable-dev-shm-usage")  # Avoid memory issues

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://web.whatsapp.com")
    print("Please scan the QR code to log in.")

    time.sleep(10)  # Wait for the page to load completely

    while True:
        try:
            print("Attempting to extract QR code...")
            # Locate the canvas element containing the QR code
            qr_canvas = driver.find_element("css selector", "canvas")

            # Take a screenshot of the canvas element
            qr_canvas.screenshot(qr_image_path)
            print(f"✅ QR Code extracted and saved at {qr_image_path}")

            # Check every 5 seconds
            time.sleep(5)  
        except Exception as e:
            print(f"❌ Error extracting QR code: {e}")
            break

    return driver

# Flask route to serve the index page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to serve the QR code image
@app.route('/qr_code')
def get_qr_code():
    if os.path.exists(qr_image_path):
        return send_file(qr_image_path, mimetype='image/png')
    else:
        return "QR Code not available yet.", 404

# Function to run the Flask server
def run_flask():
    print("Starting Flask server on http://127.0.0.1:5000/ ...")
    webbrowser.open("http://127.0.0.1:5000/")  # Open in default browser
    app.run(port=5000, debug=False, use_reloader=False)  # Disable debug

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Initialize WhatsApp and extract the QR code
    driver = init_whatsapp()
