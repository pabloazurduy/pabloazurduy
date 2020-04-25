from setuptools import find_packages
from setuptools import setup


REQUIRED_PACKAGES = ['pandas==1.0.2',
                     'mip==1.5.0',     #1.7.3 
                     'scipy==1.4.1',
                     'seaborn==0.10.0'
                     ]

setup(
    name='qp-mip',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='a linealization example of a quadratic function'
)
