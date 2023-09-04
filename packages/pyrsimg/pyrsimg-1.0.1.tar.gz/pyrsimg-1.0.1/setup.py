## author: xin luo
## creat: 2023.9.1
## des: setting for the python package


from setuptools import setup
from setuptools import find_packages


VERSION = '1.0.1'

setup(
    name='pyrsimg',  # package name
    version=VERSION,  # package version
    description='Python toolkit for easy processing of remote sensing image',  # package description
    author='The rsipy developers',
    author_email='xinluo_xin@163.com',
    maintainer='Xin Luo',
    maintainer_email='xinluo_xin@163.com',    
    license='GPL License',
    packages=find_packages(),
    python_requires='>=3.6',                # Minimum version requirement of the package
    install_requires=[]               # Install other dependencies if any
    )




