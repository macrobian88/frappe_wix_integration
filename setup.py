# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in wix_integration/__init__.py
from wix_integration import __version__ as version

setup(
    name="wix_integration",
    version=version,
    description="Production-grade Frappe application for bidirectional sync between Wix e-commerce and ERPNext",
    author="Your Company",
    author_email="support@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    license="MIT",
    keywords="frappe erpnext wix ecommerce integration sync",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Frappe",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting", 
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ],
    python_requires=">=3.8"
)
