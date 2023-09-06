## author: xin luo
## creat: 2023.9.1
## des: setting for the python package


from setuptools import setup
from setuptools import find_packages


VERSION = '1.0.7'

setup(
    name='pyrsimg',   # package name
    version=VERSION,  # package version
    description='Python toolkit for easy processing of remote sensing image',  # package description
    author='The pyrsimg developers',
    author_email='xinluo_xin@163.com',
    maintainer='Xin Luo',
    maintainer_email='xinluo_xin@163.com',    

    license='GPL License',
    packages=find_packages(),
    install_requires=['pyproj>=3.1.0', 'torch>=2.0.1', 'scikit-learn>=1.2.2', \
                      'numpy>=1.22.0', 'opencv-python', 'matplotlib>=3.6.2', \
                      'scipy>=1.10', 'astropy>=5.1'],   ## , 'gdal>=3.5'
    python_requires='>=3.6',                # Minimum version requirement of the package
    )



