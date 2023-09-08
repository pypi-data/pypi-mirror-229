import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='argscalculator',
    version='0.0.1',
    description='Django project initialize',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Salman Latif",
    author_email="salu33956@gmail.com",
    py_modules=['argscalculator'],
    include_package_data=True,
    package_dir={'': 'src'},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.6",
    install_requires=[
        'Django>=3.8',
        'virtualenv>=20'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['argscalculator=argscalculator.index:main']
    },
)