"""A setuptools based setup module."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="security_txt_policy_server",
    version="1.0.1",
    description="Security TXT Policy Server serves `.well-known/security.txt` files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    author="William Edwards",
    author_email="support@cyberfusion.nl",
    url="https://github.com/CyberfusionIO/SecurityTXTPolicyServer",
    platforms=["linux"],
    packages=find_packages(
        include=[
            "security_txt_policy_server",
            "security_txt_policy_server.*",
        ]
    ),
    data_files=[],
    entry_points={
        "console_scripts": [
            "security-txt-policy-server=security_txt_policy_server.server:main"
        ]
    },
    install_requires=[
        "starlette==0.31.1",
        "uvicorn==0.23.2",
        "validators==0.22.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["cyberfusion", "starlette"],
    license="MIT",
)
