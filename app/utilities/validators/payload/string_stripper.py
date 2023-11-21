def string_stripper(func):
    def wrapper(*args, **kwargs):
        value = args[0]
        if not value:
            return func(*args, **kwargs)

        # Remove all extra space characters in the input string
        stripped_value = " ".join(
            [part.strip() for part in list(filter(lambda x: x != "", value.split(" ")))]
        )

        args = (stripped_value, *args[1:])
        return func(*args, **kwargs)

    return wrapper
