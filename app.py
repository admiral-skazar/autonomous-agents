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
    item = data.get('item', 'item')
    model_name = data.get('model_name', 'llama2')
    try:
        # Generate a unique conversation ID
        conversation_id = str(uuid.uuid4())

        # Initialize the conversation history
        agent_a_profile = (
            "Agent A is John, a 35-year-old watch enthusiast from New York visiting Mumbai, India. "
            "He is knowledgeable about luxury watches and is always on the lookout for a good deal. "
            "He is friendly and convincible."
        )

        agent_b_profile = (
            f"Agent B is Priya, a 40-year-old local seller from Mumbai. "
            f"She owns a rare {item}. "
            "She is aware of the value of her items and is firm but fair in negotiations."
        )

        context = (
            "Environment: John and Priya are negotiating on the bustling streets of Mumbai, Maharashtra, "
            "the finance capital of India. The air is filled with the sounds of vendors and traffic, creating a vibrant atmosphere.\n"
        )

        initial_prompt = (
            f"{agent_a_profile}\n\n"
            f"{agent_b_profile}\n\n"
            f"{context}"
            f"Item for negotiation: {item}\n\n"
            "The following is a conversation between John and Priya regarding the purchase of the item. "
            "They should negotiate the price by making offers and counteroffers and reach a deal if possible. "
            "Avoid using phrases like 'thank you' or 'purchase' unless the negotiation has concluded.\n\n"
        )

        # Store the conversation history
        conversations[conversation_id] = {
            'conversation_history': initial_prompt,
            'model_name': model_name,
            'item': item,
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
    normal_human  = torch.cuda.is_available()
    print(normal_human)
    app.run(debug=True)
