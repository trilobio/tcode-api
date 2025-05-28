import random
import string


def generate_id(length: int = 22) -> str:
    """Generate 22-length random string for use as id."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
