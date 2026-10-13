import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.config import model

if __name__ == '__main__':
    reply = model().invoke('Reply with one short sentence saying the support training model connection works.')
    print(reply.content)
    print('Reported usage:', reply.usage_metadata)
