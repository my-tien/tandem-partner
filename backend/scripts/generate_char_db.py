from dotenv import load_dotenv
from tandem.char_retrieval import generate_character_db
from pathlib import Path

if __name__ == '__main__':
    load_dotenv()
    root = Path(__file__).parent.parent
    generate_character_db(f"{root}/data/3000-traditoinal-hanzi.tsv", f"{root}/.chroma/3000-traditoinal-hanzi")