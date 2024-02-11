from langchain.memory import ChatMessageHistory
from tandem.char_retrieval_chain import get_character_list
from tandem.conversation_chain import get_tandem_partner

def run_conversation_loop(conversation_chain):
    chat_history = ChatMessageHistory()
    while True:
        message = input("[Student]: ")
        terminate = "Bye!" in message
        chat_history.add_user_message(message)
        response = conversation_chain.invoke({'input': chat_history})
        chat_history.add_ai_message(response)
        print(f"[Lang]:\n{response}")
        if terminate:
            print("\nTandem session ended.")
            break

if __name__ == '__main__':
    topic = input('Conversation topic (default: "household chores"): ') or "household chores"
    character_list = get_character_list(topic=topic)
    print("character list:",character_list)
    tandem_partner = get_tandem_partner(character_list)

    run_conversation_loop(tandem_partner)
