import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proxytoolkit",
    license='MIT',
    version='V1.0.2',
    author="Coding With Devil ( Binshan Iqbal )",
    author_email="codingwithdevil@gmail.com",
    description="Proxy Scraper and Checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codingwithdevil/ProxyToolKit.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        'beautifulsoup4',
        'bs4',
        'certifi',
        'charset-normalizer',
        'idna',
        'PyQt5',
        'PyQt5-Qt5',
        'PyQt5-sip',
        'requests',
        'soupsieve',
        'urllib3',
        'flet'
    ],
    entry_points={
        'console_scripts': [
            'ProxyToolKitGui = proxytoolkit:run_gui',
        ],
    }
)