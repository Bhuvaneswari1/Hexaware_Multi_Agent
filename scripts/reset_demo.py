"""Reset only this kit's synthetic runtime state for a repeatable classroom demo."""
import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--hour', type=int, choices=range(1, 6), required=True)
args = parser.parse_args()
folder = Path(__file__).resolve().parents[1] / 'runtime' / f'hour_{args.hour}'
if folder.exists():
    shutil.rmtree(folder)
print(f'Reset synthetic Hour {args.hour} checkpoints, profiles, metrics, index and refund ledger.')
