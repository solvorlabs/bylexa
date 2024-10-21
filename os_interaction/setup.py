from setuptools import setup, find_packages

setup(
    name="bylexa",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "websockets",
        "requests",
        "PyJWT",
        "typing_extensions",
    ],
    entry_points={
        'console_scripts': [
            'bylexa=bylexa.cli:main',
        ],
    },
    author="exploring-solver",
    description="Control your PC using Bylexa voice commands.",
    url="https://github.com/exploring-solver/bylexa",
    license="MIT",
)
