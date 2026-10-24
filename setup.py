"""Tag wheels containing the native executor for the build platform."""
from pathlib import Path
from setuptools import setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_py import build_py
import shutil


class BuildPython(build_py):
    def run(self):
        super().run()
        destination = Path(self.build_lib) / 'ai4instruments/iop/schema'
        destination.mkdir(parents=True, exist_ok=True)
        for source in Path('iop/schema').glob('*.schema.json'):
            shutil.copy2(source, destination / source.name)
        destination = Path(self.build_lib) / 'ai4instruments/iop/instruments'
        destination.mkdir(parents=True, exist_ok=True)
        for source in Path('iop/instruments').glob('*.json'):
            shutil.copy2(source, destination / source.name)


class Wheel(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        self.native = any(Path('src/ai4instruments/iop/bin').glob('iop-execd*'))
        if self.native:
            self.root_is_pure = False

    def get_tag(self):
        python, abi, platform = super().get_tag()
        return ('py3', 'none', platform) if self.native else (python, abi, platform)


setup(cmdclass={'bdist_wheel': Wheel, 'build_py': BuildPython})
