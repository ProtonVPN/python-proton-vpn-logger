#!/usr/bin/env python

from setuptools import setup, find_namespace_packages

setup(
    name="proton-vpn-logger",
    version="0.2.1",
    description="Proton Technologies VPN Logging library",
    author="Proton Technologies",
    author_email="contact@protonmail.com",
    url="https://github.com/ProtonMail/proton-vpn-logger",
    install_requires=["proton-core"],
    extras_require={
        "development": ["pytest", "pytest-cov", "pylint", "flake8"]
    },
    packages=find_namespace_packages(include=['proton.vpn.logging*']),
    include_package_data=True,
    python_requires=">=3.8",
    license="GPLv3",
    platforms="Linux",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Security",
    ]
)
