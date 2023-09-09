from setuptools import setup, find_packages

setup(
    name="http-crud-sdk",
    version="1.0.0",
    description="A great CRUD SDK",
    author="LEstevalor",
    author_email="25348891955@qq.com",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LEstevalor/HttpCRUDUtils",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
