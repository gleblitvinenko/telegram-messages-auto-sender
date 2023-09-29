import random
import re


def random_choice(text: str) -> str:
    res = re.sub(r"{(.+?)}", lambda x: random.choice(x.group(1).split("|")), text)
    return res
