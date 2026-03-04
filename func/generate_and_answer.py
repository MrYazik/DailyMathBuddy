import random
import json
from pathlib import Path

if (__name__ == "__main__"):
    from func.data_base.create_db import get_level
else:
    from func.data_base.create_db import get_level
# from aiogram import Router, types
# from aiogram.filters import Command

# router = Router()

# @router.message()
# async def cmd_start(message: types.Message):
#     await message.answer("Привет!")

path = Path(__file__).parent.parent
makets_messages = ""

with open(path / 'assets' / 'messages' / 'math_op.json') as f:
    makets_messages = json.load(f)

    print(path)

def generate_math(level: str) -> str:
    if (level == 'kid'):
        one_number = random.randint(1, 10)
        two_number = random.randint(1, 10)
    elif (level == 'middle'):
        one_number = random.randint(3, 9)
        two_number = random.randint(3, 9)

        if (one_number == two_number):
            one_number = random.randint(3, 9)
            two_number = random.randint(3, 9) 
    elif (level == 'hard'):
        one_number = random.randint(3, 99)
        two_number = random.randint(3, 99)

    math_questions = makets_messages['ru']['x'].format(a=one_number, b = two_number)
    return {"quest": math_questions, "a": one_number, "b": two_number}

if __name__ == "__main__":
    while True:
        generate_number = generate_math()
        print(generate_number['quest'])

        inp_number = int(input())

        a = int(generate_number['a'])
        b = int(generate_number['b'])
        c = a * b

        if (inp_number == c):
            print("------------")
            print(makets_messages['ru']['correct'].format(a=a, b=b, c=c))
            print("------------")
            print()
        else:
            print("------------")
            print(makets_messages['ru']['not_correct'].format(a=a, b=b, c=c))
            print("------------")
            print()
