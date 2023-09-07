
def autoreload(module=None):
    import types

    try:
        from IPython import get_ipython
    except ImportError:
        print('Run in IPython')
        return

    # https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html
    if module is None:
        module = __name__
    elif isinstance(module, types.ModuleType):
        module = module.__name__

    ipy = get_ipython()
    if 'IPython.extensions.autoreload' not in ipy.extension_manager.loaded:
        ipy.run_line_magic('load_ext', 'autoreload')

    ipy.run_line_magic('autoreload', '1')
    ipy.run_line_magic('aimport', module)


class StopExecution(Exception):

    def _render_traceback_(self):
        pass
