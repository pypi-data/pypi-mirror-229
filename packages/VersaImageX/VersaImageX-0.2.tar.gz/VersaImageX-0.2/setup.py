from setuptools import setup, find_packages

setup(
    name='VersaImageX',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'Pillow',
    ],
    description='A Python library for image format conversion using Pillow.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Monir Hossain',
    author_email='monirhossain0954@gmail.com',
    url='https://github.com/MonirH533/VersaImageX',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
