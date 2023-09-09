def say_hello(name: str) -> str:
    """
    Generate a greeting message.

    Args:
        name (str): The name of the person to greet.

    Returns:
        str: A greeting message in the format "Hello, {name}".

    Example:
        >>> say_hello("John")
        'Hello, John'
    """
    return f"Hello, {name}"
