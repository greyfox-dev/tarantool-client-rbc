import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tarantoolrbc",
    version="0.0.2",
    author="RBC",
    author_email="vlatish@rbc.ru",
    description="tarantool client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greyfox-dev/tarantool-client-rbc",
    packages=setuptools.find_packages(),
    license="BSD",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Unix",
    ],
    install_requires=['tarantool'],
    python_requires='>=3.6.0, <4',
)
