import pathlib
import tempfile

CONFIG = {
    "config": {
        "default": None,
        "help": "Load extra options from a configuration file onto hub.OPT.salt_sls",
    },
    "sls": {
        "default": None,
        "help": "A space delimited list of sls refs to execute",
    },
    "cachedir": {
        "default": str(pathlib.Path(tempfile.gettempdir()) / "salt"),
        "help": "A user-writeable cache dir for the minion process",
    },
    "minion_opts": {
        "default": {},
        "type": dict,
        "help": "Overrides for the default minion opts",
    },
}


CLI_CONFIG = {
    "config": {"options": ["-c"]},
    "sls": {"positional": True},
    "cachedir": {},
}


DYNE = {"salt_sls": ["salt_sls"]}
