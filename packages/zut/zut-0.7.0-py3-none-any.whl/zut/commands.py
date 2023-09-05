"""
Add and execute commands easily, based on argparse.
Usefull for non-Django applications.
For Django applications, use including command management instead.
"""
from __future__ import annotations
from contextlib import nullcontext

import logging
from argparse import Action, ArgumentParser, Namespace, RawTextHelpFormatter, _SubParsersAction
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
import sys
from types import FunctionType, GeneratorType, ModuleType
from typing import Any, Callable, Sequence

from .logging import configure_logging
from .process import get_exit_code

logger = logging.getLogger(__name__)


def add_func_command(parser: ArgumentParser|_SubParsersAction[ArgumentParser], func: FunctionType, add_arguments: FunctionType = None, *, name: str = None, doc: str = None, defaults: dict[str,Any] = {}):
    """
    Add the given function as a subcommand of the parser.
    """
    if name is None:
        name = func.__name__
    if doc is None:
        doc = func.__doc__

    subparsers = _get_subparsers(parser)
    cmdparser = subparsers.add_parser(name, help=get_help_text(doc), description=get_description_text(doc), formatter_class=RawTextHelpFormatter)
    cmdparser.set_defaults(func=func, **defaults)

    if add_arguments:
        add_arguments(cmdparser)

    return cmdparser


def add_module_command(parser: ArgumentParser|_SubParsersAction[ArgumentParser], module: str|ModuleType, *, name: str = None, doc: str = None, defaults: dict[str,Any] = {}):
    """
    Add the given module as a subcommand of the parser.
    
    The command function must be named `handler` and the arguments definition function, if any, must be named `add_arguments`.
    """
    if not isinstance(module, ModuleType):
        module = import_module(module)

    func = getattr(module, 'handle')
    add_arguments = getattr(module, 'add_arguments', None)

    if name is None:
        name = module.__name__.split(".")[-1]
        if name.endswith('cmd') and len(name) > len('cmd'):
            name = name[0:-len('cmd')]
    
    if doc is None and hasattr(module, '__description__'):
        doc = getattr(module, '__description__')
    
    add_func_command(parser, func, add_arguments=add_arguments, name=name, doc=doc, defaults=defaults)


def add_package_commands(parser: ArgumentParser|_SubParsersAction, package: str):
    """
    Add all modules in the given package as subcommands of the parser.
    """
    package_spec = find_spec(package)
    if not package_spec:
        raise KeyError(f"package not found: {package}")
    if not package_spec.origin:
        raise KeyError(f"not a package: {package} (did you forget __init__.py ?)")
    package_path = Path(package_spec.origin).parent
    
    for module_path in package_path.iterdir():
        if module_path.is_dir() or module_path.name.startswith("_") or not module_path.name.endswith(".py"):
            continue

        module = module_path.stem
        add_module_command(parser, f"{package}.{module}")


def _get_subparsers(parser: ArgumentParser) -> _SubParsersAction[ArgumentParser]:
    """
    Get or create the subparsers object associated with the given parser.
    """
    if isinstance(parser, _SubParsersAction):
        return parser
    elif parser._subparsers is not None:
        return next(filter(lambda action: isinstance(action, _SubParsersAction), parser._subparsers._actions))
    else:
        return parser.add_subparsers(title='commands')


def get_help_text(docstring: str):
    if docstring is None:
        return None
    
    docstring = docstring.strip()
    try:
        return docstring[0:docstring.index('\n')].strip()
    except:
        return docstring


def get_description_text(docstring: str):
    if docstring is None:
        return None
    
    docstring = docstring.replace('\t', ' ')
    lines = docstring.splitlines(keepends=False)

    min_indent = None
    for line in lines:
        lstriped_line = line.lstrip()
        if lstriped_line:
            indent = len(line) - len(lstriped_line)
            if min_indent is None or min_indent > indent:
                min_indent = indent
    
    description = None
    for line in lines:
        description = (description + '\n' if description else '') + line[min_indent:]

    return description


class ArgumentManager:
    def __init__(self):
        self._registered_resources: dict[str,ArgumentResource] = {}
        self._used_resources: list[ArgumentResource] = []
        self._args: dict[str,Any] = None


    def register(self, dest: str, builder: Callable[[str],Any], metavar: str = None, default: str = None, help: str = None):
        if dest in self._registered_resources:
            raise ValueError(f"resource already defined: {dest}")
        
        self._registered_resources[dest] = ArgumentResource(dest, builder, metavar=metavar, default=default, help=help)


    def get_action(self, dest: str):
        return self._registered_resources[dest].get_action()
    

    def prepare_args(self, args: Namespace|dict):
        if isinstance(args, Namespace):
            self._args = vars(args)
        else:
            self._args = args
        
        for dest, resource in self._registered_resources.items():
            if dest in self._args:
                self._args[dest] = resource.get(self._args[dest])
                if not resource in self._used_resources:
                    self._used_resources.append(resource)
        
        return self


    def __enter__(self):
        if self._args is None:
            raise ValueError('prepare_args must be called first')
        return self._args


    def __exit__(self, exc_type, exc_value, traceback):
        for instance in self._used_resources:
            instance.close(exc_type, exc_value, traceback)


class ArgumentResource:
    def __init__(self, dest: str, builder: Callable[[Any],Any], metavar: str = None, default: str = None, help: str = None):
        self.dest = dest
        self.builder = builder
        self.metavar = metavar
        self.default = default
        self.help = help
        self._built: dict[Any,Any] = {}


    def get_action(self):
        class ResourceAction(Action):
            def __init__(a_self, option_strings, **kwargs):            
                kwargs['dest'] = self.dest
                if not 'default' in kwargs and self.default is not None:
                    kwargs['default'] = self.default
                if not 'metavar' in kwargs and self.metavar is not None:
                    kwargs['metavar'] = self.metavar
                if not 'help' in kwargs and self.help is not None:
                    kwargs['help'] = self.help
                super().__init__(option_strings, **kwargs)

            def __call__(a_self, parser: ArgumentParser, namespace: Namespace, values: str | Sequence[Any] | None, option_string: str | None = None):
                setattr(namespace, self.dest, values)
        
        return ResourceAction


    def get(self, arg_value: Any):
        if not arg_value in self._built:
            result = self.builder(arg_value)
            if isinstance(result, GeneratorType):
                result = [instance for instance in result]
            self._built[arg_value] = result
        
        return self._built[arg_value]
        

    def close(self, exc_type, exc_value, traceback):
        def close_list(instances: list):
            for instance in instances:
                if isinstance(instance, list):
                    close_list(instance)
                else:
                    # actual closing
                    if hasattr(instance, '__exit__'):
                        instance.__exit__(exc_type, exc_value, traceback)
                    elif hasattr(instance, 'close'):
                        instance.close()

        close_list(self._built)


def main(module: ModuleType, manager: ArgumentManager = None):
    """
    A default `main` function for applications.

    Commands are defined in the module's top-level namespace (i.e. __init__.py)
    using `handle` and `add_arguments` functions.

    Compatible with nested subcommands.

    Usage example:

    ```py
    import sys
    from zut import main

    if __name__ == '__main__':
        main(sys.modules[__name__])
    ```
    """
    configure_logging()

    # Determine module containing `add_arguments` and `handle`
    if module.__name__ == '__main__':
        module = import_module(".", package=module.__package__)
    else:
        raise ValueError(f"main function should be used in __main__ module")
    
    # Determine parameters
    handle = getattr(module, 'handle', None)
    add_arguments = getattr(module, 'add_arguments', None)
    version_module, version = get_module_version(module)

    if hasattr(module, '__description__'):
        description = module.__description__
    elif handle:
        description = handle.__doc__
    else:
        description = None
    
    # Build argument parser
    parser = ArgumentParser(prog=module.__name__, description=get_description_text(description), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=f"{version_module} {version or ''}")

    if add_arguments:
        add_arguments(parser)

    # Parse command line
    with manager.prepare_args(parser.parse_args()) if manager else nullcontext(vars(parser.parse_args())) as args:
        func = args.pop('func', None)

        if not func:
            if handle:
                func = handle
            else:
                logger.error("no command given")
                exit(1)

        # Run command
        try:
            r = func(**args)
            r = get_exit_code(r)
        except BaseException as err:
            message = str(err)
            logger.exception(f"exiting on {type(err).__name__}{f': {message}' if message else ''}")
            r = 1
        exit(r)


def get_module_version(module: ModuleType) -> tuple[str,str]:
    """
    Search the first of the module or module's parents which contains a __version__ attribute.

    Return a tuple containing found module and its version.
    """
    try:
        return module.__name__, getattr(module, '__version__')
    except AttributeError:
        module_parts = module.__name__.split('.')
        if len(module_parts) <= 1:
            return None, None
        parent_module = sys.modules['.'.join(module_parts[:-1])]
        return get_module_version(parent_module)
