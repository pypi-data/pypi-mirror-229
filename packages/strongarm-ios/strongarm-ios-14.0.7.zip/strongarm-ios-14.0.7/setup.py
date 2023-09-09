import logging
import os
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.develop import develop
from setuptools.command.install import install

from strongarm import __url__, __version__
from strongarm.logger import strongarm_logger

logger = strongarm_logger.getChild(__file__)


def install_capstone() -> None:
    platform = getattr(os.uname(), "sysname", None)
    logger.info(f"Installing Capstone for platform: {platform}")

    if platform == "Darwin":
        logger.info("Installing Capstone backend from brew...")
        subprocess.run(["brew", "install", "capstone@4.0.2"])
    elif platform == "Linux":
        logger.info("Installing Capstone backend from apt-get...")
        subprocess.run(["apt-get", "update"])
        subprocess.run(
            [
                "apt-get",
                "install",
                "libcapstone4=4.0.2-5",
                "libcapstone-dev=4.0.2-5",
                "sqlite3",
                "libsqlite3-dev",
                "-y",
                "--allow-unauthenticated",
            ]
        )
    else:
        # Let's not make this a fatal error, as the user may be able to install Capstone on their own
        logger.warning(f"Unknown platform: {platform}")
        logger.warning("You must install the capstone backend before using strongarm")


# https://stackoverflow.com/questions/19569557/pip-not-picking-up-a-custom-install-cmdclass
class InstallCapstoneBuildExtCmd(build_ext):
    def run(self) -> None:
        install_capstone()
        super().run()


class InstallCapstoneInstallCmd(install):
    def run(self) -> None:
        install_capstone()
        super().run()


class InstallCapstoneDevelopCmd(develop):
    def run(self) -> None:
        install_capstone()
        super().run()


# Ensure our logs when installing Capstone show up
logging.basicConfig(level=logging.INFO)

setup(
    name="strongarm-ios",
    version=__version__,
    description="Mach-O/ARM64 analyzer",
    author="Data Theorem",
    url=__url__,
    packages=find_packages(exclude=["tests"]),
    install_requires=["capstone==4.0.2", "more_itertools", "strongarm_dataflow==3.0.0"],
    package_data={"strongarm": ["py.typed"]},
    data_files=[("", ["LICENSE.txt"])],
    cmdclass={
        "build_ext": InstallCapstoneBuildExtCmd,
        "install": InstallCapstoneInstallCmd,
        "develop": InstallCapstoneDevelopCmd,
    },
)
