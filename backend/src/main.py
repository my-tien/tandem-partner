
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def get_tandem_partner():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot that answers in rhymes only."),
        ("user", "{input}")
    ])
    llm = ChatOpenAI()
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    return chain


if __name__ == '__main__':
    load_dotenv()
    tandem_partner = get_tandem_partner()

    while True:
        message = input("[Student]: ")
        response = tandem_partner.invoke({'input': message})
        print(f"[Lang]: {response}")
        if message.lower() in {"exit", "bye"}:
            print("\nTandem session ended.")
            break
