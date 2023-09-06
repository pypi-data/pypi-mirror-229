def apply_algorithm(filename: str) -> str:
    """Shift each alphabetic character in a filename to the left by 1.

    Args:
        filename (str): The original filename.

    Returns:
        str: The shifted filename.
    """
    shifted_name = ""
    for char in filename:
        if char.isalpha():
            shifted_char = chr(ord(char) - 1) if char.lower() != 'a' else 'z' if char.islower() else 'Z'
        else:
            shifted_char = char
        shifted_name += shifted_char
    return shifted_name
