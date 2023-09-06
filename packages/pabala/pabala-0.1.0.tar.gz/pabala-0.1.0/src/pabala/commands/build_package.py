from typing import List

from pabala.command import BuildCommand, Argument, FlagArgument
from pabala.result import Result


class BuildPackage(BuildCommand):
    source_dirname: str
    package_name: str
    ignore: List[str]

    @property
    def arguments(self) -> List[Argument]:
        return [
            Argument("name", help="References to a package name in pyproject.toml under deployment.packages section"),
            FlagArgument("all", help="build all groups defined in pyproject.toml"),
            Argument("skip", help="groups to skip comma separated, default is empty"),
            FlagArgument("ignore-lock", help="do not use poetry.lock file"),
            Argument("python", help="python version used to build the layer, default is 3.9", default="3.9"),
        ]


class BuildPackageHandler:

    def __call__(self, command: BuildPackage) -> Result:
        return Result.success()
