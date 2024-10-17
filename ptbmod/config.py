from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    HANDLER: list[str] = getenv("HANDLER", "/ !").split()
    devs_env = getenv("DEVS")
    DEVS: list[int] = []
    if devs_env:
        try:
            DEVS = list(map(int, devs_env.split()))
        except ValueError:
            print("Warning: Some values in DEVS could not be converted to integers.")
