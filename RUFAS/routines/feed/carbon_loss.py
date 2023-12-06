def update_all(storage):
    """
    Description:
        The only external function call. Runs the carbon loss sub-module
        "pseudocode_feed" F.1.3

    Args:
        storage: the storage receptacle for which loss is being calculated
    """

    harvest_loss(storage)

    storage_loss(storage)

    feed_out_loss(storage)

    update_carbon(storage)


def harvest_loss(storage):
    """
    Description:
        Carbon loss during harvest
        "pseudocode_feed" F.1.3

    Args:
        storage
    """

    storage.C_harvest_gas = storage.C * storage.C_harvest_gas_percent

    storage.C_harvest_particle = storage.C * storage.C_harvest_particle_percent


def storage_loss(storage):
    """
    Description:
        Carbon loss during feed storage
        "pseudocode_feed" F.1.3

    Args:
        storage
    """

    storage.C_storage_gas = storage.C * storage.C_storage_gas_percent

    storage.C_storage_leachate = storage.C * storage.C_storage_leachate_percent


def feed_out_loss(storage):
    """
    Description:
        Carbon loss during feed out
        "pseudocode_feed" F.1.3

    Args:
        storage
    """

    storage.C_feed_out_gas = storage.C * storage.C_feed_out_gas_percent

    storage.C_feed_out_particle = storage.C * storage.C_feed_out_particle_percent


def update_carbon(storage):
    """
    Description:
        Update stored carbon based on calculated losses
        "pseudocode_feed" F.1.3

    Args:
        storage
    """

    storage.C_loss = (storage.C_harvest_gas + storage.C_harvest_particle +
                      storage.C_storage_gas + storage.C_storage_leachate +
                      storage.C_feed_out_gas + storage.C_feed_out_particle)

    storage.C -= storage.C_loss

    storage.DM -= storage.C_loss
