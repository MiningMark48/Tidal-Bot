import os.path as osp
import toml

def get_extensions():
    extensions_path = "extensions.toml"
    exts = []

    if osp.isfile(extensions_path):
        with open(extensions_path, 'r') as file:
            data = toml.load(file)

            for cat in data:
                for e in data[cat]:
                    exts.append(e if cat == "none" else f"{cat}.{e}")

    return exts
