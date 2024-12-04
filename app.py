from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask API!"

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"name": "Aditya", "role": "Developer"}
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.json  # Get JSON payload
    response = {"message": "Data received", "received_data": data}
    return jsonify(response)
