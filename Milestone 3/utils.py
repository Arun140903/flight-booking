import random
import string
def generate_pnr() -> str:
    letters = string.ascii_uppercase
    digits = string.digits
    return "".join(random.choices(letters + digits, k=8))