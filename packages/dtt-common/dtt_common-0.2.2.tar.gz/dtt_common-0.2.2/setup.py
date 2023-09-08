from setuptools import find_packages, setup

setup(
    name='dtt_common',
    version='0.2.2',
    packages=find_packages(),
    install_requires=[
        # Add any dependencies your package requires here
        'selenium>=4.0',
        'pytest>=7.4.2',
        'imutils>=0.5',
        'opencv-python>=4.8.0.0',
        'scikit-image>=0.21.0',        
        # Other dependencies
    ],
)