import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="cipherspy",
    version="0.0.2",
    author="Fathi AbdelMalek",
    author_email="abdelmalek.fathi.2001@gmail.com",
    url="https://github.com/fathiabdelmalek/cryptopy.git",
    description="Strong Passwords Generator made with python.",
    license="OSI Approved :: MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['cipherspy', 'cipherspy.cipher'],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ]
)
