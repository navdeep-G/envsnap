from setuptools import setup
from setuptools.command.install import install
import subprocess


class CustomInstallCommand(install):
    """Custom installation command to set up shell autocompletion."""

    def run(self):
        print("Running custom install: setting up envsnap completion...")
        super().run()
        try:
            subprocess.run(["envsnap", "--setup-completion"], check=True)
        except Exception as e:
            print(f"⚠️ Warning: Autocompletion setup failed: {e}")


setup(
    name="envsnap",
    version="0.1.0",
    packages=["envsnap"],
    entry_points={
        "console_scripts": ["envsnap=envsnap.__main__:main"]
    },
    cmdclass={
        "install": CustomInstallCommand,
    },
    python_requires=">=3.6",
    description="Snapshot and restore your development environment easily",
    author="Your Name",
    license="Apache 2.0",
)
