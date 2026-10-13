import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.config import runtime_dir
from common.knowledge import KnowledgeBase

if __name__ == '__main__':
    kb = KnowledgeBase(runtime_dir(3))
    print(json.dumps({'embedding_backend':kb.backend,
                      'results':kb.search('damaged replacement policy')}, indent=2))
