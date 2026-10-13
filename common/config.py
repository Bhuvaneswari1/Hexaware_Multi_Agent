import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
DATA = ROOT / 'data'


def runtime_dir(hour: int) -> Path:
    base = Path(os.getenv('DESK_RUNTIME_DIR', str(ROOT / 'runtime')))
    folder = base / f'hour_{hour}'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def model():
    from langchain_openai import ChatOpenAI
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError('Live mode needs OPENAI_API_KEY in the root .env file.')
    return ChatOpenAI(model=os.getenv('LLM_MODEL', 'gpt-4.1-mini'),
                      temperature=0, timeout=25, max_retries=1)
