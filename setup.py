import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="django_mysql_multiprocessing",
    version="0.0.1",
    author="PoCheng Huang",
    author_email="pcghuang@gmail.com",
    description="Django MySQL Database Connections for multiprocessing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/envive/django_mysql_multiprocessing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
