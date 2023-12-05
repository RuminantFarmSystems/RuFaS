def update_all(storage):
    """
    Description:
        The only external function call. Runs the nitrogen loss sub-module
        "pseudocode_feed" F.1.3

    Args:
        storage: the storage receptacle for which loss is being calculated
    """
    CP_loss(storage)

    NPN_loss(storage)

    update_CP(storage)


def CP_loss(storage):
    """
    Description:
        Crude protein loss to gas and leaching
        "pseudocode_feed" F.1.3

    Args:
        storage
    """

    storage.CP_gas = storage.CP * storage.CP_gas_percent

    storage.CP_leachate = storage.CP * storage.CP_leachate_percent


def NPN_loss(storage):
    """
    Description:
        Non-Protein-Nitrogen loss
        "pseudocode_feed" F.1.3

    Args:
        storage
    """

    storage.NPN += storage.CP * storage.NPN_min_percent


def update_CP(storage):
    """
    Description:
        Account for crude protein loss in relevant pools
        "pseudocode_feed" F.1.3

    Args:
        storage
    """
    storage.CP_loss = storage.CP_gas + storage.CP_leachate

    storage.CP -= storage.CP_loss
    storage.DM -= storage.CP_loss
