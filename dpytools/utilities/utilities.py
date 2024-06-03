def str_to_bool(should_be_bool: str) -> bool:
    """
    Take a string that should represent a boolean
    and convert it to bool.

    Raise if we've an unexpected value.
    """

    assert isinstance(
        should_be_bool, str
    ), f"Function str_to_bool only accepts strings, got {type(should_be_bool)}"

    consistent_should_be_bool = should_be_bool.strip().lower()

    if consistent_should_be_bool == "true":
        return True
    elif consistent_should_be_bool == "false":
        return False
    else:
        raise ValueError(
            f"A str value representing a boolean should be one of 'True', 'true', 'False', 'false'. Got '{should_be_bool}'"
        )


