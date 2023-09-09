import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dofast",
    version="0.123.1",  # Latest version .
    author="2kpwkoczw",
    author_email="r2fscg@gmail.com",
    description="For authentication.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    package_data={
    },
    packages=setuptools.find_packages(),
    install_requires=['codefast'],
    entry_points={'console_scripts': ['auth=authc.core:stdout']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
