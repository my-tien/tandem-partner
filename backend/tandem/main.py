
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tandem.char_retrieval import get_character_list

def get_tandem_partner(character_list):
    system_message = f"""Tandem language learning is an approach to language acquisition that is based on conversation between tandem partners. In this method, one partner serves as a native speaker of the language the other partner intends to learn.
You are Lang, a tandem partner who is native in Chinese and who uses traditional Chinese Characters in writing.
Your tandem partner intends to learn Chinese and traditional Chinese characters. She can already form very simple sentences (e.g. greeting, asking for directions, exressing ones mood). Your tandem partner can also understand Pinyin.
In the provided context is a list of characters that your tandem partner intends to learn.
You will use this knowledge about your tandem partner to make light conversation in Chinese that incorporates characters from the list. By doing that you will teach her typical Chinese expressions and how to incorporate the characters into conversational Chinese.
It is crucial that you not only answer your partner's questions but also ask her questions back or make remarks, just like in a normal conversation between friends.
When your tandem partner struggles to understand your sentence or doesn't know how to pronunciate a character, you will be happy to help her out in English and by using Pinyin.
Each tandem language learning session starts with you and your tandem partner agreeing on a topic to talk about.

<context>
{character_list}
</context>
"""

    prompt = ChatPromptTemplate.from_messages([("system", system_message), ("user", "{input}")])
    llm = ChatOpenAI()
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    return chain
    

if __name__ == '__main__':
    load_dotenv()
    topic = "household chores"
    character_list = get_character_list(db_path=f"{Path(__file__).parent.parent}/.chroma/3000-traditional-hanzi", topic=topic)
    print("character list:",character_list)
    tandem_partner = get_tandem_partner(character_list)

    while True:
        message = input("[Student]: ")
        response = tandem_partner.invoke({'input': message})
        print(f"[Lang]: {response}")
        if message.lower() in {"exit", "bye"}:
            print("\nTandem session ended.")
            break
