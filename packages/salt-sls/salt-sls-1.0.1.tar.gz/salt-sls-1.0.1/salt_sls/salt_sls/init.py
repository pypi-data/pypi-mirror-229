def __init__(hub):
    # Add a sub for all the imports to go onto
    hub.pop.sub.add(dyne_name="lib")

    # Add all the python libraries used by this project
    hub.pop.sub.add(python_import="copy", sub=hub.lib)
    hub.pop.sub.add(python_import="pathlib", sub=hub.lib)

    # Ignore all deprecation warnings
    hub.pop.sub.add(python_import="warnings", sub=hub.lib)
    hub.lib.warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Add salt onto hub.lib
    hub.pop.sub.add(dyne_name="salt", sub=hub.lib)
    hub.pop.sub.add(python_import="salt.config", subname="config", sub=hub.lib.salt)
    hub.pop.sub.add(python_import="salt.cli.caller", subname="caller", sub=hub.lib.salt)


def cli(hub):
    """
    Start the sls command on the cli
    """
    # Load the config for salt-sls onto hub.OPT
    hub.pop.config.load(["salt_sls"], cli="salt_sls")

    # Gather the default minion opts
    opts = hub.lib.copy.deepcopy(hub.lib.salt.config.DEFAULT_MINION_OPTS)

    # Override the default cachedir in /var/log with one that doesn't need root or permission changes
    opts["cachedir"] = hub.OPT.salt_sls.cachedir

    # Allow the salt-lss config file to override any minion opts
    opts.update(hub.OPT.salt_sls.minion_opts)

    # Hard override some of the minion options
    opts["file_client"] = "local"
    opts["local"] = True
    opts["print_metadata"] = False

    # Interpret the first CLI argument as a path to an SLS file
    sls_path = hub.lib.pathlib.Path(hub.OPT.salt_sls.sls).absolute()
    assert sls_path.exists()

    # Add the parent of the input SLS file as a file root
    opts["file_roots"] = {"base": [str(sls_path.parent)]}
    opts["arg"] = [sls_path.stem]
    opts["fun"] = "state.apply"

    hub.log.debug(f"File roots: {opts['file_roots']}")

    # Run agentless salt locally
    caller = hub.lib.salt.caller.Caller.factory(opts)
    caller.run()
