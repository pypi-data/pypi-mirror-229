from setuptools import setup

setup(
    name='school-log',
    version='1.4',
    packages=['slog'],
    entry_points={
        "console_scripts": [
            "slog=slog.slog:main"
        ]
    },
    install_requires=[
        'requests'
    ]
)