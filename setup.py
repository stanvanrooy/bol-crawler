import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="bol-crawler", # Replace with your own username
    version="0.0.1",
    author="Stan van Rooy",
    author_email="stan@rooy.works",
    description="A simple package for crawling bol.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stanvanrooy/bol-crawler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)