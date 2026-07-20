import pandas as pd

def make_info_map(module, caller, variable, **grouping_variables):
    return dict(
        module=module, caller=caller, variable=variable, **grouping_variables
    )


def _tuplize_info_map(info_map: dict, extract: bool = True) -> tuple:
    if not extract:
        info_map = info_map.copy()
    out_tuple = (
        info_map.pop("module"), info_map.pop("caller"), info_map.pop("variable")
    )
    return out_tuple


def rufas_add_to_pool(t: int, info_map: dict, value, pool: dict):
    map_copy: dict = info_map.copy()

    key = f"{map_copy.get("module")}.{info_map.get("caller")}.{map_copy.get("variable")}"
    element = value.copy
    if not key in pool:
        pool[key]["values"] = []
        pool[key]["info_maps"] = []
    pool[key]["values"].append(element)
    pool[key]["info_maps"].append(map_copy)

    # TODO: add proxy for the original add_to_pool method
    pass


def rufas_fill_pool():
    # TODO: add a proxy for the original pool filling method
    pass


def tidy_add_to_pool(t: int, info_map: dict, value, pool: dict):
    map_copy: dict = info_map.copy()
    key = _tuplize_info_map(map_copy)
    element = dict(time=t, value=value, **map_copy)
    if not key in pool:
        pool[key] = []
    pool[key].append(element)

def tidy_fill_pool(
        info_maps: list[dict], ntime: int = 100, pool: dict = None, inplace=False
) -> dict:
    if pool is None:
        pool = {}
    else:
        pool = pool if inplace else pool.copy()

    for i, imap in enumerate(info_maps):
        for t in range(ntime):
            # skip even time steps for the last sixth of cases:
            if (i > len(info_maps) // 6) and (t % 2 == 0):
                continue
            x = (i + 1 * t * 0.1) + (i * 0.2)  # nonsense data that depends on i and t
            tidy_add_to_pool(t, info_map=imap, value=x, pool=pool)
    return pool


def frame_variable(module: str, caller: str, variable: str, values: list[dict]):
    data_frame = pd.DataFrame(values)
    # add address columns:
    data_frame[["module", "caller", "variable"]] = (module, caller, variable)
    return data_frame


def frame_pool(filled_pool: dict):
    return [frame_variable(*k, values=v) for k, v in filled_pool.items()]


def stack_frames(df_list: list[pd.DataFrame]):
    return pd.concat(df_list).reset_index(drop=True)


def tidy_frame(stacked: pd.DataFrame):
    # get group column names:
    addr = ["module", "caller", "time"]
    var, val = ("variable", "value")
    groups = [col for col in stacked.columns if col not in addr + [var, val]]
    index_cols = addr + groups
    # pivot to wide form:
    tidied = stacked.pivot(index=index_cols, columns=var, values=val)
    # get rid of the "variable" column index name:
    tidied = tidied.rename_axis(None, axis=1).sort_index()
    return tidied

if __name__ == "__main__":



    cases = [
        make_info_map("HerdManager", "measure_consumption", "total_mass_consumed"),
        make_info_map("FieldManager", "apply_manure", "manure_mass_added", field="A"),
        make_info_map(
            "FieldManager", "measure_crops", "nitrogen", field="A", crop="corn"
        ),
        make_info_map(
            "FieldManager", "measure_crops", "carbon", field="A", crop="corn"
        ),
        make_info_map(
            "FieldManager", "measure_crops", "nitrogen", field="A", crop="alfalfa"
        ),
        make_info_map(
            "FieldManager", "measure_crops", "carbon", field="A", crop="alfalfa"
        ),
        make_info_map(
            "FieldManager", "measure_crops", "nitrogen", field="B", crop="alfalfa"
        ),
        make_info_map(
            "FieldManager", "measure_crops", "carbon", field="B", crop="alfalfa"
        ),
    ]

    cases_df = pd.DataFrame(cases).rename_axis("case")

    filled_pool = tidy_fill_pool(cases, ntime=3)

    df_list = frame_pool(filled_pool)

    stacked = stack_frames(df_list)

    tidy_df = tidy_frame(stacked)

    print(tidy_df.reset_index())

    # ----

    big_pool = tidy_fill_pool(cases, ntime=10000)
    big_list = frame_pool(big_pool)
    big_stacked = stack_frames(big_list)
    big_tidy = tidy_frame(big_stacked)

    from pympler.asizeof import asizeof

    sizes = pd.Series({
        "pool dictionary": asizeof(big_pool),
        "data frame list": asizeof(big_list),
        "long stacked data frame": asizeof(big_stacked),
        "long stacked data frame (``pandas`` estimate)": sum(big_stacked.memory_usage(deep=True)),
        "tidy stacked data frame": asizeof(big_tidy),
        "tidy stacked data frame (``pandas`` estimate)": sum(big_tidy.memory_usage(deep=True)),
    })