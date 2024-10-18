from setuptools import setup, find_packages
setup(
    name="bylexa",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "click",        # For CLI functionality
        "websockets",   # For WebSocket communication
        "requests",     # For making HTTP API calls
        "typing-extensions",  # Optional for typing hints in some Python versions
        "PyJWT",
    ],
    entry_points={
        'console_scripts': [
            'bylexa=bylexa.cli:main',
        ],
    },
    author="exploring-solver",
    description="A Python package for controlling your PC using Bylexa voice commands.",
    url="https://github.com/exploring-solver/bylexa",  # Update this with your actual GitHub repo URL
    license="MIT",
)
