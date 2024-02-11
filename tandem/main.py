
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from tandem.char_retrieval_chain import get_character_list
from tandem.conversation_chain import get_contextualizer_chain, get_tandem_partner

def run_conversation_loop(conversation_chain):
    chat_history = []
    contextualizer = get_contextualizer_chain()
    while True:
        message = input("[Student]: ")
        terminate = "Bye!" in message
        if len(chat_history) > 0:
            message = contextualizer.invoke({"input": message, "chat_history": chat_history})
            print(f"[Student (contextualized)]: {message}")
        response = conversation_chain.invoke({'input': message})
        chat_history.extend([HumanMessage(content=message), AIMessage(content=response)])
        print(f"[Lang]:\n{response}")
        if terminate:
            print("\nTandem session ended.")
            break

if __name__ == '__main__':
    load_dotenv(override=True)
    topic = input('Conversation topic (default: "household chores"): ') or "household chores"
    character_list = get_character_list(topic=topic)
    print("character list:",character_list)
    tandem_partner = get_tandem_partner(character_list)

    run_conversation_loop(tandem_partner)
