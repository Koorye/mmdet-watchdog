import argparse
import importlib
from stats.stats import Stats


parser = argparse.ArgumentParser()
parser.add_argument('--config', help='config file path')
args = parser.parse_args()

config_path = args.config
assert config_path.endswith('.py')
print(f'Config Path: {config_path}')
config_path = config_path.replace('\\', '/')
config_path = config_path[2:] if config_path.startswith('./') else config_path
config_path = config_path[:-3].replace('/', '.')

cfg = importlib.import_module(config_path).Config()
stats = Stats(cfg)
stats.stat_and_draw()
