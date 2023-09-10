"""Recursively reload modules/subpackages of a given package.

The original code from Ipython.lib.deepreload distributed under BSD license
is modified to only reload modules from the target package.
"""

from __future__ import annotations

import builtins
import importlib
import sys
import types
from contextlib import contextmanager
from types import ModuleType
from typing import Mapping, Optional, Sequence
from warnings import warn


@contextmanager
def replace_import_hook(import_func):
    original_import_func = builtins.__import__
    try:
        builtins.__import__ = import_func
        yield
    finally:
        builtins.__import__ = original_import_func


def get_parent(
    globals: Mapping[str, object] | None, level: int
) -> tuple[Optional[ModuleType], str]:
    """
    parent, name = get_parent(globals, level)

    Return the package that an import is being performed in.  If globals comes
    from the module foo.bar.bat (not itself a package), this returns the
    sys.modules entry for foo.bar.  If globals is from a package's __init__.py,
    the package's entry in sys.modules is returned.

    If globals doesn't come from a package or a module in a package, or a
    corresponding entry is not found in sys.modules, None is returned.
    """
    orig_level = level

    if not level or not isinstance(globals, dict):
        return None, ""

    pkgname = globals.get("__package__", None)

    if pkgname is not None:
        # __package__ is set, so use it
        if not hasattr(pkgname, "rindex"):
            raise ValueError("__package__ set to non-string")
        assert isinstance(pkgname, str)
        if len(pkgname) == 0:
            if level > 0:
                raise ValueError("Attempted relative import in non-package")
            return None, ""
        name = pkgname
    else:
        # __package__ not set, so figure it out and set it
        if "__name__" not in globals:
            return None, ""
        modname = globals["__name__"]
        assert isinstance(modname, str)

        if "__path__" in globals:
            # __path__ is set, so modname is already the package name
            globals["__package__"] = name = modname
        else:
            # Normal module, so work out the package name if any
            lastdot = modname.rfind(".")
            if lastdot < 0 < level:
                raise ValueError("Attempted relative import in non-package")
            if lastdot < 0:
                globals["__package__"] = None
                return None, ""
            globals["__package__"] = name = modname[:lastdot]

    dot = len(name)
    for x in range(level, 1, -1):
        try:
            dot = name.rindex(".", 0, dot)
        except ValueError as e:
            raise ValueError(
                "attempted relative import beyond top-level " "package"
            ) from e
    name = name[:dot]

    try:
        parent = sys.modules[name]
    except BaseException as e:
        if orig_level < 1:
            warn(
                "Parent module '%.200s' not found while handling absolute "
                "import" % name
            )
            parent = None
        else:
            raise SystemError(
                "Parent module '%.200s' not loaded, cannot "
                "perform relative import" % name
            ) from e

    # We expect, but can't guarantee, if parent != None, that:
    # - parent.__name__ == name
    # - parent.__dict__ is globals
    # If this is violated...  Who cares?
    return parent, name


def load_next(
    mod: Optional[ModuleType], altmod: Optional[ModuleType], name: str, buf: str
):
    """
    mod, name, buf = load_next(mod, altmod, name, buf)

    altmod is either None or same as mod
    """
    if len(name) == 0:
        # completely empty module name should only happen in
        # 'from . import' (or '__import__("")')
        return mod, None, buf

    dot = name.find(".")
    if dot == 0:
        raise ValueError("Empty module name")

    if dot < 0:
        subname = name
        next = None
    else:
        subname = name[:dot]
        next = name[dot + 1 :]

    if buf != "":
        buf += "."
    buf += subname

    result = import_submodule(mod, subname, buf)
    if result is None and mod != altmod:
        result = import_submodule(altmod, subname, subname)
        if result is not None:
            buf = subname

    if result is None:
        raise ImportError("No module named %.200s" % name)

    return result, next, buf


def add_submodule(
    mod: Optional[ModuleType], submod: Optional[ModuleType], fullname: str, subname: str
):
    """mod.{subname} = submod"""
    if mod is None:
        return  # Nothing to do here.

    if submod is None:
        submod = sys.modules[fullname]

    setattr(mod, subname, submod)

    return


def ensure_fromlist(mod: ModuleType, fromlist: Sequence[str], buf: str, recursive: int):
    """Handle 'from module import a, b, c' imports."""
    if not hasattr(mod, "__path__"):
        return
    for item in fromlist:
        if not hasattr(item, "rindex"):
            raise TypeError("Item in ``from list'' not a string")
        if item == "*":
            if recursive:
                continue  # avoid endless recursion
            try:
                all = mod.__all__
            except AttributeError:
                pass
            else:
                ret = ensure_fromlist(mod, all, buf, 1)
                if not ret:
                    return 0
        elif not hasattr(mod, item):
            import_submodule(mod, item, buf + "." + item)


def custom_import(
    name: str,
    globals: Mapping[str, object] | None = None,
    locals: Mapping[str, object] | None = None,
    fromlist: Sequence[str] = (),
    level: int = 0,
) -> ModuleType:
    """Import a module. The signature of this function is the same as builtins.__import__
    for overriding purposes.
    """
    parent, buf = get_parent(globals, level)

    head, name, buf = load_next(parent, None if level < 0 else parent, name, buf)

    tail = head
    while name:
        tail, name, buf = load_next(tail, tail, name, buf)

    # If tail is None, both get_parent and load_next found
    # an empty module name: someone called __import__("") or
    # doctored faulty bytecode
    if tail is None:
        raise ValueError("Empty module name")

    if not fromlist:
        return head

    ensure_fromlist(tail, fromlist, buf, 0)
    return tail


RELOAD_PACKAGE: list[str] = []
EXACT_EXCLUDE_PACKAGE: tuple[str, ...] = (
    *sys.builtin_module_names,
    "sys",
    "os.path",
    "builtins",
    "__main__",
)
PREFIX_EXCLUDE_PACKAGE: tuple[str, ...] = ("numpy", "pandas")
VERBOSE: bool = True
modules_reloading = {}
# Need to keep track of what we've already reloaded to prevent cyclic evil
found_now = {}


def import_submodule(mod: ModuleType, subname: str, fullname: str):
    """m = import_submodule(mod, subname, fullname)"""
    # Require:
    # if mod == None: subname == fullname
    # else: mod.__name__ + "." + subname == fullname
    global found_now, VERBOSE

    if fullname in found_now and fullname in sys.modules:
        return sys.modules[fullname]

    if not does_it_need_reload(fullname):
        if fullname not in sys.modules:
            m = importlib.import_module(subname, mod)
            found_now[fullname] = 1
            add_submodule(mod, m, fullname, subname)
        else:
            m = sys.modules[fullname]

        return m

    if VERBOSE:
        print("Reloading", fullname)
    found_now[fullname] = 1
    oldm = sys.modules.get(fullname, None)
    try:
        if oldm is not None:
            m = importlib.reload(oldm)
        else:
            m = importlib.import_module(subname, mod)
    except:
        # load_module probably removed name from modules because of
        # the error.  Put back the original module object.
        if oldm:
            sys.modules[fullname] = oldm
        raise

    add_submodule(mod, m, fullname, subname)
    return m


def custom_reload(m: ModuleType):
    """Replacement for reload()."""
    # Hardcode this one  as it would raise a NotImplementedError from the
    # bowels of Python and screw up the import machinery after.
    # unlike other imports the `exclude` list already in place is not enough.

    if m is types:
        return m
    if not isinstance(m, ModuleType):
        raise TypeError("reload() argument must be module")

    name = m.__name__

    if name not in sys.modules:
        raise ImportError("reload(): module %.200s not in sys.modules" % name)

    global modules_reloading
    try:
        return modules_reloading[name]
    except:
        modules_reloading[name] = m

    try:
        newm = importlib.reload(m)
    except:
        sys.modules[name] = m
        raise
    finally:
        modules_reloading.clear()
    return newm


def reload(
    pkg: str,
    allow_reload: Optional[str] | list[str] = None,
    exact_exclude: tuple[str, ...] = EXACT_EXCLUDE_PACKAGE,
    prefix_exclude: tuple[str, ...] = PREFIX_EXCLUDE_PACKAGE,
    verbose: bool = True,
) -> ModuleType:
    """Reload a package and all dependencies it has imported.

    # Arguments
        pkg: The package to reload.
        exclude: A list of modules to exclude from reloading.
        allow_reload: A list of modules / or single module to allow reloading.
            If None, it will be the package itself. To allow reloading everything,
            use empty string

    # Returns
        The reloaded package.

    # Common mistakes:

    ```python
    deepreload.reload('sm')
    ```

    It will try to reload `sm.__init__`. As `sm.__init__` does not import
    anything, nothing will be reloaded (including the whole package `sm`)

    ```python
    deepreload.reload('sm.prelude')
    ```

    The module `sm.prelude` imports other dependencies from `sm.*` sub-packages.
    Since `allow_reload` default is the package itself, `sm.*` sub-packages do not
    match and nothing will be reloaded. To make it work, use `deepreload.reload('sm.prelude', allow_reload='sm')`
    """
    if pkg not in sys.modules:
        raise ImportError(f"Module {pkg} is not imported yet.")

    global found_now, RELOAD_PACKAGE, PREFIX_EXCLUDE_PACKAGE, VERBOSE
    for i in exact_exclude:
        found_now[i] = 1

    VERBOSE = verbose
    PREFIX_EXCLUDE_PACKAGE = prefix_exclude

    if allow_reload is None:
        RELOAD_PACKAGE = [pkg]
    elif isinstance(allow_reload, str):
        RELOAD_PACKAGE = [allow_reload]
    else:
        RELOAD_PACKAGE = allow_reload

    try:
        with replace_import_hook(custom_import):
            return custom_reload(sys.modules[pkg])
    finally:
        found_now = {}


def does_it_need_reload(fullname: str):
    global RELOAD_PACKAGE, PREFIX_EXCLUDE_PACKAGE

    return any(
        fullname == x or fullname.startswith(x + ".") for x in RELOAD_PACKAGE
    ) and not any(
        fullname == x or fullname.startswith(x + ".") for x in PREFIX_EXCLUDE_PACKAGE
    )
