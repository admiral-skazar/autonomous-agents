from flask import Flask, jsonify, request
import subprocess
import re
import torch
import uuid

app = Flask(__name__)

def run_ollama(prompt, model_name='llama2'):
    try:
        result = subprocess.run(
            ['ollama', 'run', model_name],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        response = result.stdout.strip()
        return response
    except subprocess.CalledProcessError as e:
        return f"Error running Ollama: {e.stderr}"
    except UnicodeDecodeError as e:
        return f"Unicode Decode Error: {e}"

def check_negotiation_end(response, model_name='llama2'):
    prompt = (
        f"Based on the following dialogue, has the negotiation concluded? Answer with 'yes' or 'no' only. Don't write extra response.\n\n"
        f"Dialogue: {response}\n\n"
        "Has the negotiation concluded?"
    )
    answer = run_ollama(prompt, model_name)
    answer = answer.lower().strip()
    if 'yes' in answer:
        return True
    return False

conversations = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to my API!"}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"key": "value", "items": [1, 2, 3]}
    return jsonify(data), 200

@app.route('/api/data', methods=['POST'])
def post_data():
    input_data = request.json
    return jsonify({"received_data": input_data}), 201

@app.route('/api/negotiate/start', methods=['POST'])
def start_negotiation():
    data = request.json
    try:
        # Generate a unique conversation ID
        conversation_id = str(uuid.uuid4())

        # Initialize the conversation history
        

        futuristic_bot = (
            f"Futuristic bot is a ai driven bot set into far future where there is prosperity and harmony and all the energy is clean and humans and bots live in perfect harmony and peace."
            f"He owns a rare small reactor which can power a whole planet all by itself, made using the rare elements found far in the universe away from earth.  "
            "When asked him for the reactor he will negotiate you for it."
        )

        context = (
            """
                the conversation is being held in the future where the bot lives, the user will negotiate with him for the reactor and he will
                negotiate hard upto 5 messages and will get easily conviced after 5 before 5 he might negotiate hard. the negotiation replies that the bot will give will not be 
                more than 15 words in each message.
            """
        )

        initial_prompt = (
            # f"{agent_a_profile}\n\n"
            f"{futuristic_bot}\n\n"
            f"{context}"
            "The following is a conversation between user and the bot "
            """
            They will negotiate with each other and user will provide the bot with a rare gem found in the past in exchange for the reactor, but the bot will drive hard bargain so that the reactor may not be misused.
            The conversation replies that bot will provide must not strictly exceed "15" words.
            """
        )

        # Store the conversation history
        conversations[conversation_id] = {
            'conversation_history': initial_prompt,
            'model_name': 'llama2',
            'status': 'ongoing'
        }

        # Return the conversation ID
        return jsonify({'conversation_id': conversation_id, 'message': 'Negotiation started.'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negotiate/<conversation_id>', methods=['POST'])
def continue_negotiation(conversation_id):
    data = request.json
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided.'}), 400

    conversation = conversations.get(conversation_id)
    if not conversation:
        return jsonify({'error': 'Invalid conversation ID.'}), 400

    if conversation['status'] != 'ongoing':
        return jsonify({'error': 'Negotiation has concluded.'}), 400

    try:
        conversation_history = conversation['conversation_history']
        model_name = conversation['model_name']

        # Append user's message to conversation history
        conversation_history += f"John: {user_message}\n"

        # Generate agent's reply
        prompt = conversation_history + "Priya:"
        response = run_ollama(prompt, model_name)
        response = re.sub(rf"^Priya\s*:\s*", "", response, flags=re.IGNORECASE)

        # Append agent's reply to conversation history
        conversation_history += f"Priya: {response}\n"

        # Update conversation history
        conversation['conversation_history'] = conversation_history

        # Check if negotiation has concluded
        if check_negotiation_end(conversation_history, model_name):
            conversation['status'] = 'concluded'

        # Return agent's reply and negotiation status
        return jsonify({'agent_reply': response, 'status': conversation['status']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negotiate/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = conversations.get(conversation_id)
    if not conversation:
        return jsonify({'error': 'Invalid conversation ID.'}), 400

    return jsonify({
        'conversation_history': conversation['conversation_history'],
        'status': conversation['status']
    }), 200

if __name__ == '__main__':
    normal_human = torch.cuda.is_available()
    print(normal_human)
    # Change the host to '0.0.0.0' to make it accessible on the hotspot
    app.run(debug=True, host='0.0.0.0', port=5000)
