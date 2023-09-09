import json
from os.path import join, exists


def read_config(ds_path, ds):
    config = dict()
    cf = join(ds_path, ds, f"{ds}_config.json")
    assert exists(cf), f'Config file for dataset {ds} not found'
    with open(cf, errors='ignore') as f:
        conf = json.load(f)
        config['object_class_names'] = [c["name"] for c in conf["structures"]["list"]]
        config['object_parents'] = [c["parentStructure"] for c in conf["structures"]["list"]]
    return config


def dict_val_to_list(dict_in):
    for key, val in dict_in.items():
        dict_in[key] = arg_to_list(val)
    return dict_in


def arg_to_list(arg_in):
    if isinstance(arg_in, list):
        return arg_in
    else:
        return [arg_in]
