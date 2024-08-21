def sum_aggregator(data: list[float]) -> float:
    """
    Returns the sum of a list of numbers.

    Parameters
    ----------
    data : List[float]
        A list of numbers whose sum is to be calculated.

    Returns
    -------
    float
        The sum of the input numbers.
    """
    return sum(data)


try:
    data = sum_aggregator([3, float('nan'), 5])
except ValueError as e:
    print(f"i'm gonna return none because of {e}")

print("reached the end")
