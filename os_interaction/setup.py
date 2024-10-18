from setuptools import setup, find_packages

setup(
    name="bylexa",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "websockets",
        "click",
    ],
    entry_points={
        'console_scripts': [
            'bylexa=bylexa.cli:main',
        ],
    },
    author="exploring-solver",
    description="A Python package for controlling your PC using Bylexa voice commands.",
    url="https://github.com/exploring-solver/bylexa",  # Update this with the actual URL
    license="MIT",
)
