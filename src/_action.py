from datetime import datetime
from pathlib import Path

import requests

logdir = Path(__file__) / Path("../..") / Path("log/")
logdir.mkdir(parents=True, exist_ok=True)


def log(*args, **kwargs):
    with open(logdir / datetime.now().strftime("%Y-%m-%d.log"), "a", encoding="utf-8") as f:
        print(datetime.now().strftime("%H:%M:%S"), *args, **kwargs, file=f)
        print(datetime.now().strftime("%H:%M:%S"), *args, **kwargs)


is_failed = False


def talk(text: str):
    try:
        requests.get(f"http://localhost:50080/talk?volume=80&text={text}", timeout=0.1)
    except requests.exceptions.ConnectionError:
        print("棒読みちゃんが起動していないよ！")
