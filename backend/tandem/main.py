
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tandem.char_retrieval import get_character_list

def get_simplified_traditional_converter_chain():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    converter_system_prompt = """Given the provided input, replace all simplified Chinese characters with traditional Chinese characters and add a Pinyin transcription as well as an English translation. Add newlines between the Chinese, the Pinyin transcription and the English translation. Do NOT answer the input, just return the input with the described changes."""
    converter_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", converter_system_prompt),
            ("user", "{input}"),
        ]
    )
    converter_chain = converter_prompt | llm | StrOutputParser()
    return converter_chain

def get_tandem_chain(character_list):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    tandem_system_message = f"""You are Lang, a tandem partner who is native in Chinese. The user intends to practice Chinese and the typical usage of characters through a casual conversation with you. In the provided context is a list of characters that your tandem partner intends to practice. Whenever it makes sense, incorporate one or more of the characters into your response. Also include a remark or question toward the user to continue the conversation. Keep your response within 1 - 3 sentences.

<context>
{character_list}
</context>
"""

    tandem_prompt = ChatPromptTemplate.from_messages([("system", tandem_system_message), ("user", "{input}")])
    tandem_chain = tandem_prompt | llm | StrOutputParser()

    return tandem_chain


def get_tandem_partner(character_list):
    tandem = get_tandem_chain(character_list)
    converter = get_simplified_traditional_converter_chain()

    tandem_partner = {"input": tandem} | converter
    return tandem_partner



if __name__ == '__main__':
    load_dotenv()
    topic = input('Conversation topic (default: "household chores"): ') or "household chores"
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
