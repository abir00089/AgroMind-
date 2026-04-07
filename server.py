from flask import Flask, request, jsonify

app = Flask(__name__)

sensor_data = {}

@app.route('/data', methods=['POST'])
def receive_data():
    global sensor_data
    sensor_data = request.json
    print("Received:", sensor_data)
    return jsonify({"status": "ok"})

# 🔥 ADD THIS
@app.route('/get-data')
def get_data():
    return sensor_data

# 🔥 Optional (for testing)
@app.route('/')
def home():
    return "Server is running 🚀"

app.run(host='0.0.0.0', port=5000)
