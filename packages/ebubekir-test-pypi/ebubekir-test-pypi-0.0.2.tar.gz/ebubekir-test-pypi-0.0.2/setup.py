from setuptools import setup, find_packages
from distutils.util import convert_path

def get_version():
    ver_path = convert_path("ebubekir-test-pypi/__version__.py")
    with open(ver_path) as ver_file:
        main_ns = {}
        exec(ver_file.read(), main_ns)
        return main_ns["__version__"]

setup(
    name="ebubekir-test-pypi",
    author_email="karanfilebubekir@gmail.com",
    author="Ebubekir Karanfil",
    description="Test PyPi publising",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    version=get_version(),
    packages=find_packages(),
    install_requires=['']
)