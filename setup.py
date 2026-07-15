from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="rentpro",
    version="0.1.0",
    description="Paperless ERP for Moroccan car rental agencies",
    author="Rent Pro",
    author_email="dev@rentpro.ma",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
