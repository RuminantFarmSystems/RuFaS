class GeneralValidator:
    """
    A class used to validate general data.

    The general behavior of the methods in this class is to raise an exception if the data is not valid.

    """
    @staticmethod
    def check_type(instance: object, expected_type: type) -> None:
        """
        Check if an instance is of the expected type.

        Parameters
        ----------
        instance : object
            The instance to check.
        expected_type : type
            The expected type of the instance.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the instance is not of the expected type.

        """
        try:
            assert isinstance(instance, expected_type)
        except AssertionError:
            raise TypeError(f'Expected type {expected_type}, got {type(instance)}.')
