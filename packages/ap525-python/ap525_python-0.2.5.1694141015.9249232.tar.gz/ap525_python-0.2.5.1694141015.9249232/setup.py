import os
import shutil
import time

from setuptools import setup, find_packages
from setuptools.command.install import install

now_time = str(time.time())
ver = '0.2.5.' + now_time


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        # Copy files to D drive root after installing the package
        src_dir = os.path.join(os.getcwd(), 'ap525_python', 'ap', 'ap_dll')  # Specify your source directory here
        dest_dir = 'D:\\'  # D drive root as the destination directory
        for file_name in os.listdir(src_dir):
            if file_name.endswith('.dll'):
                shutil.copy2(os.path.join(src_dir, file_name), os.path.join(dest_dir, file_name))


setup(
    name='ap525_python',
    version=ver,
    description='ap python',
    author='hewitt',
    author_email='pypi_user@163.com',
    license='MIT',
    packages=find_packages(),
    package_data={'ap525_python': ['ap/ap_dll/*.dll']},
    install_requires=['pythonnet', 'pyserial', 'PyVISA', 'pandas', 'psutil'],  # List all dependencies here
    cmdclass={
        'install': PostInstallCommand,
    }
)
