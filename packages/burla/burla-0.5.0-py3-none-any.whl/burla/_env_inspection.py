import subprocess
import warnings
import json
import sys
import inspect

from burla._helpers import nopath_warning

warnings.formatwarning = nopath_warning


class EnvironmentInspectionError(Exception):
    def __init__(self, stdout):
        super().__init__(
            (
                "The following error occurred attempting to get list if packages to install in "
                f"remove execution environment's: {stdout}"
            )
        )


def get_pip_packages():
    result = subprocess.run(
        ["pip", "list", "--format=json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if result.returncode != 0:
        raise EnvironmentInspectionError(result.stderr)

    for pkg in json.loads(result.stdout):
        if "+" in pkg["version"]:
            pkg["version"] = pkg["version"].split("+")[0]
        if not pkg.get("editable_project_location"):
            yield pkg


def get_function_dependencies(function_):
    """Returns python modules imported in module where `function_` is defined"""
    function_module_name = function_.__module__
    function_module = sys.modules[function_module_name]
    source = inspect.getsource(function_module)

    for line in source.split("\n"):
        if "#" in line:
            line = line.split("#")[0]

        if "from" in line:
            module = line.split("from ")[1].split(" import")[0]
            yield module.split(".")[0]
        elif "import" in line:
            yield line.split("import ")[1].split(".")[0]
