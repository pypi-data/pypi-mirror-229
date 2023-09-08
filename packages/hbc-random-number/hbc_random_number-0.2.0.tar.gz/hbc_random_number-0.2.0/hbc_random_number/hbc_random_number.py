"""Main module."""
import os

def generate_random_number(min_value, max_value):
    """
    Generate a random number within a given range.

    Parameters:
    min_value (int): The minimum value of the range.
    max_value (int): The maximum value of the range.

    Returns:
    int: A randomly generated number within the specified range.
    """
    num_bytes = (max_value - min_value).bit_length() // 8 + 1

    random_bytes = os.urandom(num_bytes)
    random_value = int.from_bytes(random_bytes, 'big') % (max_value - min_value + 1) + min_value

    return random_value
