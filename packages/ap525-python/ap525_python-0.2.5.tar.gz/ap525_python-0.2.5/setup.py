from setuptools import setup, find_packages
from setuptools.extension import Extension

setup(
    name='ap525_python',
    version='0.2.5',
    description='ap python',
    author='hewitt',
    author_email='pypi_user@163.com',
    license='MIT',
    packages=find_packages(),
    package_data={'ap525_python': ['ap/ap_dll/*.dll']},
    install_requires=['pythonnet', 'pyserial', 'PyVISA', 'pandas', 'psutil'],  # List all dependencies here
)
