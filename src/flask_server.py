from flask import Flask, request, jsonify
from utils.mqtt import MQTT_CLIENT
from config.topics import topics
import atexit

# Create a Flask app instance
app = Flask(__name__)

topic_data = {}

def on_message(client, userdata, message):
    raw_value = message.payload.decode("utf-8")
    print("row valeu", raw_value, type(raw_value))
    topic_obj = topics.get(message.topic) or {}
    expected_type = topic_obj.get("type", str)
    value = expected_type(raw_value)
    print("updateing value", message.topic,value)
    topic_data[message.topic] =value

mqtt_client = MQTT_CLIENT()
mqtt_client.subscribe_all_topic()
mqtt_client.client.on_message = on_message
mqtt_client.listen()

@app.route('/topic', methods=['GET'])
def get_topic():
    try:
        return jsonify({"topics": topics }), 200
    
    except Exception as e:
            return jsonify({"error": str(e)}), 500
  

@app.route('/topic/<string:topic>', methods=['GET', 'POST'])
def handle_topic(topic):
    try:
        if request.method == 'GET':
            if topic in topic_data:
                return jsonify({"topic": topic, "value": topic_data[topic] }), 200
            return jsonify({"message": "Topic not found" }), 200
        
        elif request.method == "POST":
            print("top)ic", topic_data)
            data = request.get_json()
            if 'value' not in data:
                return jsonify({"error": "Missing 'value' in the request"}), 400
            
            if topic not in topics:
                return jsonify({"error": "Unsupported topic"}), 400
            
            mqtt_client.client.publish(topic, data['value'])
            return jsonify({"message": "Data updated sucesfully"}), 200
    
    except Exception as e:
            return jsonify({"error": str(e)}), 500
    
# Run the app on the local server
if __name__ == "__main__":
    app.run(debug=False)

atexit.register(mqtt_client.disconnect())