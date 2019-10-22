from unittest import main
from RUFAS.test.animal import test_lactating_cow

def run_tests():
    print('Running animal tests...')
    test = main(module=test_lactating_cow, exit=False)
    print()