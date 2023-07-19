from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop


class Alfalfa(BaseCrop):
    """Alfalfa class"""
    def __init__(self, crop_name, data):
        """create an instance of Alfalfa
                    
           Args: 
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="alfalfa")

    # species-specific methods ...

class CerealRye(BaseCrop):
    """CerealRye class"""
    def __init__(self, crop_name, data):
        """create an instance of CerealRye

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="cereal_rye")

    # species-specific methods ...

class Corn(BaseCrop):
    """Corn class"""
    def __init__(self, crop_name, data):
        """create an instance of Corn
                    
           Args: 
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="corn")

    # species-specific methods ...

class FallOats(BaseCrop):
    """FallOats class"""
    def __init__(self, crop_name, data):
        """create an instance of FallOats

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="fall_oats")

    # species-specific methods ...

class Potato(BaseCrop):
    """Potato class"""
    def __init__(self, crop_name, data):
        """create an instance of Potato

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="potato")

    # species-specific methods ...


class Soybean(BaseCrop):
    """SoyBean class"""
    def __init__(self, crop_name, data):
        """create an instance of SoyBean

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="soybean")

    # species-specific methods ...


class SpringBarley(BaseCrop):
    
    """`SpringBarley class"""
    def __init__(self, crop_name, data):
        """create an instance of SpringBarley

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="spring_barley")

    # species-specific methods ...

class SpringWheat(BaseCrop):
    """SpringWheat class"""
    def __init__(self, crop_name, data):
        """create an instance of SpringWheat

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="spring_wheat")

    # species-specific methods ...

class SugarBeet(BaseCrop):
    """SugarBeet class"""
    def __init__(self, crop_name, data):
        """create an instance of SugarBeet

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="sugar_beet")

    # species-specific methods ...


class TallFescue(BaseCrop):
    """TallFescue class"""
    def __init__(self, crop_name, data):
        """create an instance of TallFescue

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="tall_fescue")

    # species-specific methods ...


class Triticale(BaseCrop):
    """Triticale class"""
    def __init__(self, crop_name, data):
        """create an instance of Triticale

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="triticale")

    # species-specific methods ...


class WinterWheat(BaseCrop):
    """WinterWheat class"""
    def __init__(self, crop_name, data):
        """create an instance of winter wheat

           Args:
            crop_name (str): the name of the crop
            data (dict): data used to construct the class
        """
        super().__init__(crop_name=crop_name, data=data, species="winter_wheat")

    # species-specific methods ...
