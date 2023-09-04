import os.path

from setuptools import find_packages, setup

long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

setup(
    name='hexprint',
    version='0.1',
    author='Adam Rimon',
    author_email='',
    description='A simple utility Python module to visually work with bytes in a useful way ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Prilkop/hexprint',
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
