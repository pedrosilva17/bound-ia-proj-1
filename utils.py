def parse_int_input(message: str, lower_bound: int = 0, upper_bound: int = 999) -> int:
    while True:
        try:
            num = int(input(message))
            if num in range(lower_bound, upper_bound + 1):
                break
            print("Not a valid option.")
        except ValueError:
            print("Not an integer.")
    return num