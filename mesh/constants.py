from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.joinpath('data')

USER_MAPPING_FILE = DATA_DIR.joinpath('usermapping')
CONFIG_FILE = BASE_DIR.joinpath('config')
