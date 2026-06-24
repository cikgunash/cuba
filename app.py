import os
import base64
import smtplib
from flask import Flask, render_template_string, request, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# ================= CONFIGURATION =================
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Your 16-character Google App Password
RECEIVER_EMAIL = "nash.mansor@gmail.com"
# =================================================

HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Camera Emailer</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 40px; background: #f4f4f9; }
        video, canvas { border: 2px solid #333; border-radius: 8px; background: #000; max-width: 90%; }
        button { padding: 12px 24px; font-size: 16px; font-weight: bold; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 15px; }
        button:hover { background: #0056b3; }
        #status { margin-top: 15px; font-weight: bold; color: #555; }
    </style>
</head>
<body>
    <h2>Flask Webcam Snap & Email</h2>
    
    <video id="video" width="400" height="300" autoplay></video><br>
    <button id="snap">Capture & Send Email</button>
    
    <div id="status"></div>

    <canvas id="canvas" width="400" height="300" style="display:none;"></canvas>

    <script>
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const snapBtn = document.getElementById('snap');
        const statusDiv = document.getElementById('status');

        // Request access to the webcam
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => { video.srcObject = stream; })
            .catch(err => { 
                statusDiv.innerText = "Error: Webcam access denied or unavailable.";
                console.error(err); 
            });

        // Trigger when button is clicked
        snapBtn.addEventListener('click', () => {
            statusDiv.innerText = "Capturing image...";
            
            // Draw the current video frame onto the hidden canvas
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, 400, 300);
            
            // Convert canvas image to base64 string
            const imageData = canvas.toDataURL('image/jpeg');

            statusDiv.innerText = "Sending payload to server...";

            // Send base64 image data to Flask backend
            fetch('/send-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: imageData })
            })
            .then(response => response.json())
            .then(data => {
                statusDiv.innerText = data.message || data.error;
            })
            .catch(err => {
                statusDiv.innerText = "Error communicating with server.";
                console.error(err);
            });
        });
    </script>
</body>
</html>
"""

def email_file(file_path):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "Flask Camera Snapshot"
    
    msg.attach(MIMEText("Here is the picture taken automatically from the Flask app UI interface.", 'plain'))
    
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= snapshot.jpg")
    msg.attach(part)
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/send-email', methods=['POST'])
def send_email_route():
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"error": "No image data received"}), 400

        # Strip header from the base64 URL scheme
        header, encoded = image_data.split(",", 1)
        decoded_image = base64.b64decode(encoded)

        # Temp save the picture on server
        temp_filename = "snap_temp.jpg"
        with open(temp_filename, "wb") as f:
            f.write(decoded_image)

        # Trigger email function
        email_file(temp_filename)

        # Clean up local file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        return jsonify({"message": "Success! Email sent to " + RECEIVER_EMAIL})

    except Exception as e:
        return jsonify({"error": f"Server failed processing: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
