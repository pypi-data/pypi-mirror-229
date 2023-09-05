from setuptools import setup, find_packages

setup(
    name='whatupworld',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'whatupworld = whatupworld:say_what_up',
        ],
    }
)
