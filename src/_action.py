from datetime import datetime
from pathlib import Path

import requests

logdir = Path(__file__) / Path("../..") / Path("log/")
logdir.mkdir(parents=True, exist_ok=True)


def log(*args, **kwargs):
    with open(logdir / datetime.now().strftime("%Y-%m-%d.log"), "a") as f:
        print(datetime.now().strftime("%H:%M:%S"), *args, **kwargs, file=f)
        print(datetime.now().strftime("%H:%M:%S"), *args, **kwargs)


def talk(text: str):
    requests.get(f"http://localhost:50080/talk?volume=80&text={text}")
