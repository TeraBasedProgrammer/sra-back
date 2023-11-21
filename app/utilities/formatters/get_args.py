import inspect


def get_args(stack_depth: int = 1, slice: int = 0) -> str:
    """Converts funtion parameters in log-fiendly form

    Args:
        stack_depth (int): defines from what call from the stack should arguments be extracted.
        Defaults to 1
        slice (int): slice index to remove unnecessary args from the response

    Returns:
        str: formatted string
    """
    # Get service parameters from call stack
    stack = inspect.stack()
    caller_frame = stack[stack_depth][0]
    args, _, _, values = inspect.getargvalues(caller_frame)

    printed_args = []
    for arg in args:
        if arg != "self":
            printed_args.append(f'"{arg}" -> {values[arg]}')

    return "\n".join(printed_args[slice:])
