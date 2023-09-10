from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="datamuse-python",
    version="1.3.7",
    description="A collection of functions using the Datamuse API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Animesh Srivastava",
    author_email="animeshsrivastava2003@email.com",
    packages=find_packages(),
    install_requires=[
        'requests>=2.0.0',
        'beautifulsoup4>=4.0.0',
    ],
    url='https://github.com/Animesh0203/datamuse-python',
)
