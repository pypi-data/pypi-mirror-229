from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="fastpy-rest",
    version="0.1.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.1.1"
    ],
    author="Shashi Kant",
    author_email="shashikantrbl123@gmail.com",
    url="https://github.com/sineshashi/FastPy-Rest",
    description="FastPy-Rest is a minimalisitc lightweight framework to create restapis easily.",
    long_description=long_description,
    long_description_content_type="markdown"
)
