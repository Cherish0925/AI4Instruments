"""Tag wheels containing the native executor for the build platform."""
from pathlib import Path
from setuptools import setup
from setuptools.command.bdist_wheel import bdist_wheel


class Wheel(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.native = any(Path('src/ai4instruments/iop/bin').glob('iop-execd*'))
        if self.native:
            self.root_is_pure = False

    def get_tag(self):
        python, abi, platform = super().get_tag()
        return ('py3', 'none', platform) if self.native else (python, abi, platform)


setup(cmdclass={'bdist_wheel': Wheel})
