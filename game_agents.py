import subprocess
import re

def run_ollama(prompt, model_name='llama2'):
    """
    Runs the Ollama model with the given prompt and returns the response.
    """
    try:
        result = subprocess.run(
            ['ollama', 'run', model_name],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',  # Ensure UTF-8 encoding
            errors='replace',  # Replace undecodable bytes
            check=True
        )
        response = result.stdout.strip()
        return response
    except subprocess.CalledProcessError as e:
        print(f"Error running Ollama: {e.stderr}")
        return ""
    except UnicodeDecodeError as e:
        print(f"Unicode Decode Error: {e}")
        return ""

def check_negotiation_end(response, model_name='llama2'):
    """
    Checks if the negotiation has concluded by asking the model.
    Returns True if concluded, False otherwise.
    """
    prompt = (
        f"Based on the following dialogue, has the negotiation concluded? Answer with 'yes' or 'no' only dont write extra response.\n\n"
        f"Dialogue: {response}\n\n"
        "Has the negotiation concluded?"
    )
    answer = run_ollama(prompt, model_name)
    answer = answer.lower().strip()
    # print("ANSWER" , answer)
    if 'yes' in answer:
        return True
    return False

def simulate_negotiation(item, model_name='llama2'):
    # Agent Profiles
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

    # Context Setup
    context = (
        "Environment: John and Priya are negotiating on the bustling streets of Mumbai, Maharashtra, "
        "the finance capital of India. The air is filled with the sounds of vendors and traffic, creating a vibrant atmosphere.\n"
    )

    # Initial Prompt
    initial_prompt = (
        f"{agent_a_profile}\n\n"
        f"{agent_b_profile}\n\n"
        f"{context}"
        f"Item for negotiation: {item}\n\n"
        "The following is a conversation between John and Priya regarding the purchase of the item. "
        "They should negotiate the price by making offers and counteroffers and reach a deal if possible. "
        "Avoid using phrases like 'thank you' or 'purchase' unless the negotiation has concluded.\n\n"
    )

    # Starting the conversation
    conversation_history = initial_prompt
    max_steps = 10  # Maximum number of exchanges

    # Start with John's greeting
    user_input = f"John: Namaste, Priya! I'm interested in buying your {item}. Is it still available?"
    print(user_input)
    conversation_history += user_input + "\n"

    for step in range(max_steps):
        # Determine the speaking agent
        agent = "Priya" if step % 2 == 0 else "John"

        # Prepare the prompt for the current agent
        prompt = conversation_history + f"{agent}:"

        # Use Ollama to generate the agent's response
        response = run_ollama(prompt, model_name)

        # Clean up the response
        # Remove any leading 'Priya:' or 'John:' to prevent duplication
        response = re.sub(rf"^{agent}\s*:\s*", "", response, flags=re.IGNORECASE)

        # Handle cases where the model might still include the agent name
        if response.lower().startswith(agent.lower()):
            response = response[len(agent):].strip()
            if response.startswith(':'):
                response = response[1:].strip()

        if not response:
            print(f"{agent}: [No response]")
            break  # End the conversation if no response is generated

        # Print and update the conversation history
        print(f"{agent}: {response}")
        conversation_history += f"{agent}: {response}\n"

        # Check if the negotiation has ended
        if check_negotiation_end(conversation_history, model_name):
            print("\nEnd of Negotiation.")
            return

    print("\nNegotiation reached the maximum number of exchanges without conclusion.")

def main():
    item = input("Enter the item for negotiation: ")
    model_name = 'llama2'  # Replace with your actual model name in Ollama
    simulate_negotiation(item, model_name)

if __name__ == "__main__":
    main()
