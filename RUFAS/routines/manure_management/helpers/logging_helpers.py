import logging

# DEBUG
# INFO
# WARNING = DEFAULT
# ERROR
# CRITICAL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(filename)s - Line %(lineno)d - '
                              '%(levelname)s - %(funcName)s \n'
                              '%(message)s \n')
file_handler = logging.FileHandler(filename='test.log', mode='w')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def add(a, b):
    return a + b


def divide(a, b):
    try:
        result = a / b
        logger.debug(f'a = {a}, b = {b}')
    except ZeroDivisionError:
        logger.error('Tried to divide by zero')
    else:
        return result


if __name__ == '__main__':
    x, y = 10, 5

    logger.debug(f'Add: {x} + {y} = {add(x, y)}')
    logger.debug(f'Divide: {5} / {0} = {divide(5, 0)}')

