algorithm_metadata = {
    "name": "example2",
    "description": "Shifts each alphabetic character in a filename to the right by 1."
}

def apply_algorithm(filename: str) -> str:
    """Shifts each alphabetic character in a filename to the right by 1.

    Args:
        filename (str): The original filename.

    Returns:
        str: The shifted filename.
    """
    shifted_name = ""
    for char in filename:
        if char.isalpha():
            shifted_char = chr(ord(char) + 1) if char.lower() != 'z' else 'a' if char.islower() else 'A'
        else:
            shifted_char = char
        shifted_name += shifted_char
    return shifted_name
