from flask import Flask, jsonify, render_template_string
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

# Data storage
data_censor = {
    "temperaturec": None,
    "humidityc": None
}

# Setting MQTT
MQTT_BROKER = "tes.humiditycTemperaturecSensor.org"
MQTT_PORT = 1888
MQTT_TEMPERATUREC = "/sensor/data/temperaturec"
MQTT_HUMIDITYC = "/sensor/data/humidityc"

# MQTT client setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(MQTT_TEMPERATUREC)
    client.subscribe(MQTT_HUMIDITYC)

def on_message(client, userdata, msg):
    global data_censor
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    if topic == MQTT_TEMPERATUREC:
        data_censor["temperaturec"] = payload
    elif topic == MQTT_HUMIDITYC:
        data_censor["humidityc"] = payload
    print(f"Message: {payload} on topic: {topic}")

MQTT_client = mqtt.Client()
MQTT_client.on_connect = on_connect
MQTT_client.on_message = on_message

def MQTT_loop():
    MQTT_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    MQTT_client.loop_forever()

mqtt_thread = threading.Thread(target=MQTT_loop)
mqtt_thread.start()

# Flask API routes
@app.route('/api/temperaturec', methods=['GET'])
def get_temperaturec():
    return jsonify({"temperaturec": data_censor["temperaturec"]})

@app.route('/api/humidityc', methods=['GET'])
def get_humidityc():
    return jsonify({"humidityc": data_censor["humidityc"]})

@app.route('/api/data_censor', methods=['GET'])
def get_data_censor():
    return jsonify(data_censor)

@app.route('/', methods=['GET'])

def home():
    return render_template_string(html_content, temperaturec=data_censor["temperaturec"], humidityc=data_censor["humidityc"])

html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv='refresh' content='4'/>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel='stylesheet' href='https://use.fontawesome.com/releases/v5.7.2/css/all.css' integrity='sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr' crossorigin='anonymous'>
    <title>ESP32 DHT Server</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(to right, #2c3e50, #bdc3c7);
            color: white;
            text-align: center;
        }
        h2 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }
        .sensor {
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem;
            width: 80%;
            max-width: 400px;
        }
        .sensor i {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        .sensor .indicator {
            font-size: 2.5rem;
        }
        .units {
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <h2>ESP32 DHT Server</h2>
    <div class="sensor">
        <i class='fas fa-thermometer-half' style='color:#ca3517;'></i>
        <div class='dht-labels'>Temperaturec</div>
        <div class='indicator'>{{ temperaturec }}</div>
        <sup class='units'>&deg;C</sup>
    </div>
    <div class="sensor">
        <i class='fas fa-tint' style='color:#00add6;'></i>
        <div class='dht-labels'>Humidityc</div>
        <div class='indicator'>{{ humidityc }}</div>
        <sup class='units'>&percnt;</sup>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)