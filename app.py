from flask import Flask, jsonify, request
import subprocess
import re

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
        f"Based on the following dialogue, has the negotiation concluded? Answer with 'yes' or 'no' only dont write extra response.\n\n"
        f"Dialogue: {response}\n\n"
        "Has the negotiation concluded?"
    )
    answer = run_ollama(prompt, model_name)
    answer = answer.lower().strip()
    if 'yes' in answer:
        return True
    return False

def simulate_negotiation(item, model_name='llama2'):
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

    conversation_history = initial_prompt
    max_steps = 10
    user_input = f"John: Namaste, Priya! I'm interested in buying your {item}. Is it still available?"
    conversation_history += user_input + "\n"

    for step in range(max_steps):
        agent = "Priya" if step % 2 == 0 else "John"
        prompt = conversation_history + f"{agent}:"
        response = run_ollama(prompt, model_name)
        response = re.sub(rf"^{agent}\s*:\s*", "", response, flags=re.IGNORECASE)

        if not response:
            return {"conversation": conversation_history, "status": "incomplete"}

        conversation_history += f"{agent}: {response}\n"

        if check_negotiation_end(conversation_history, model_name):
            return {"conversation": conversation_history, "status": "concluded"}

    return {"conversation": conversation_history, "status": "max_steps_reached"}


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

@app.route('/api/negotiate', methods=['POST'])
def negotiate():
    data = request.json
    item = data.get('item', 'item')
    model_name = data.get('model_name', 'llama2')
    try:
        result = simulate_negotiation(item, model_name)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negotiate', methods=['GET'])
def get_negotiation():
    return jsonify({"message": "Use POST /negotiate to start a negotiation."}), 200


if __name__ == '__main__':
    app.run(debug=True)