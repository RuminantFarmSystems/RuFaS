def _combine_into(d: dict, combined: dict) -> None:
    """recursively join d (dict) into combined (dict)"""
    for k, v in d.items():
        if isinstance(v, dict):
            _combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v

def nested_merge_dicts(*dicts: dict) -> dict:
    """
    recursively join dictionaries into one dictionary, where sub-dictionaries
    are properly joined.
    """

    combined = {}

    for d in dicts:
        _combine_into(d, combined)

    return combined

if __name__ == '__main__':
    # Example usage:
    import tomllib
    import pprint

    # read top-level TOML file as dictionary
    with open("user_config.toml", "rb") as f:
        main_toml = tomllib.load(f)

    # parse sub-configs if present
    if "sub_configs" in main_toml and len(main_toml["sub_configs"]) > 0:
        # read additional TOML files, from paths in sub_configs dict.
        files = [open(f, "rb") for f in main_toml["sub_configs"].values()]
        toml_dicts = [tomllib.load(f) for f in files]

        # combine all the dictionaries
        ## Note: to ensure that the top-level config (main_toml) has highest
        ## priority (values can't be overwritten), it could be the
        ## last positional argument instead of the first.
        user_input = nested_merge_dicts(main_toml, *toml_dicts)
    else:
        user_input = main_toml

    # read defaults and add in anything the user missed
    with open("_defaults.toml", "rb") as f:
        defaults = tomllib.load(f)

    all_input = nested_merge_dicts(defaults, user_input)


    # print the final joined dictionary.
    pprint.pprint(all_input, sort_dicts=False)

    # # compare keys:
    # in_both = set(user_input.keys()).intersection(set(defaults.keys()))
    # user_only = set(user_input.keys()) - set(defaults.keys())
    # default_only = set(defaults.keys()) - set(user_input.keys())
    #
    # pprint.pprint(
    #     {"user_only": user_only, "default_only": default_only, "in_both": in_both},
    #     sort_dicts = False
    # )

