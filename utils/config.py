import toml
import os
import inspect


current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)

config = toml.load(parent_dir + "/config.toml")
