
if __name__ == '__main__':
    import re
    from pprint import pprint
    from pathlib import Path
    from RUFAS.input_manager import InputManager
    import json
    import tomli_w
    import collections

    # setup parameters
    md_path = Path("input/metadata/example_freestall_dairy_metadata.json")

    # Initialize the input manager and manually load in the data.
    im = InputManager()
    im.start_data_processing(
        metadata_path=md_path,  # bypasses task manager meta data.
        input_root=Path("."),  # TODO: why isn't this the default within the function?
        task_id="random task name"  # TODO: why is this required? Should be some default.
    )

    # note that the input manager pool values can be changed in place
    print(im.pool["config"]["include_detailed_values"])
    im.pool["config"]["include_detailed_values"] = True
    print(im.pool["config"]["include_detailed_values"])

    # Keep crop and soil data
    keep_pattern = "(^config$|field.*|soil.*|crop.*|.*schedule.*|Corn*)"

    all_input_CS = {k: v for k, v in im.pool.items() if re.match(keep_pattern, k)}
    # Sort it
    all_input_CS = collections.OrderedDict(sorted(all_input_CS.items()))

    # double check I didn't miss keys
    not_kept = [k for k in im.pool.keys() if k not in all_input_CS.keys()]

    # write a json file
    json.dump(all_input_CS, open("eval_CS/inputs/all_input_CS.json", "w"), indent=4)
    # write a toml file
    tomli_w.dump(all_input_CS, open("eval_CS/inputs/all_input_CS.toml", "wb"))

