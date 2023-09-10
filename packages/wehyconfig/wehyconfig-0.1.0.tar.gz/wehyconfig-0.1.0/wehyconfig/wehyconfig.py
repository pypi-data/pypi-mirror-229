import tomllib
from pathlib import Path


def read_config(config_source: str, section=""):
    config_path = Path(config_source)
    if config_path.is_dir():
        config_files = _get_config_files(config_path)
        config = {}
        for config_file in config_files:
            config[config_file.stem] = _read_config_file(config_file)
    elif config_path.is_file():
        config = _read_config_file(config_path, section)

    return config


def _get_config_files(config_path: Path()):
    return config_path.iterdir()


def _read_config_file(config_file: Path(), section=""):
    with open(config_file, "rb") as file:
        config = tomllib.load(file)
    if section:
        config = config[section]
    return config
