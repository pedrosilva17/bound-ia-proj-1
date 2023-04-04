def parse_int_input(message: str, lower_bound: int = 0, upper_bound: int = 10000) -> int:
    """Request and parse a user's integer input, making sure it is in fact an integer 
    between the specified limit.

    Args:
        message (str): The message to show the user before it types in its input.
        lower_bound (int, optional): The minimum acceptable input. Defaults to 0.
        upper_bound (int, optional): The maximum acceptable input. Defaults to 10000.

    Returns:
        int: The number typed by the user.
    """
    while True:
        try:
            num = int(input(message))
            if num in range(lower_bound, upper_bound + 1):
                break
            print("Not a valid option.")
        except ValueError:
            print("Not an integer.")
    return num