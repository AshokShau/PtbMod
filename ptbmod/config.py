from os import getenv
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Config:
    HANDLER: List[str] = getenv("HANDLER", "/ !").split()
    devs_env = getenv("DEVS")
    DEVS: List[int] = []
    if devs_env:
        try:
            DEVS = list(map(int, devs_env.split()))
        except ValueError:
            print("Warning: Some values in DEVS could not be converted to integers.")
