from random import choice
from string import ascii_uppercase

def random_seed(number: int = 4) -> str:
	return ''.join(choice(ascii_uppercase) for i in range(number))


def random_nikcname() -> str:
	return random_seed()