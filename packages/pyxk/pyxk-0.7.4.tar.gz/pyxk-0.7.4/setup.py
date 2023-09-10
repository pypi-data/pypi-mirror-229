import setuptools


with open("README.md", "r", encoding="utf-8") as read_file_obj:
    long_description = read_file_obj.read()

setuptools.setup(
    name="pyxk",
    version="0.7.4",
    author="kai139",
    install_requires=[
        "requests",
        "pycryptodome",
        "rich",
        "m3u8",
        "aiohttp",
        "aiofiles",
        "click",
        "parsel",
        "chardet",
        "user_agents",
        "faker",
    ],
    entry_points={
        "console_scripts": [
            "m3u8 = pyxk.m3u8._entry_point:main",
            "request = pyxk.request._entry_point:main"
        ],
    },
    author_email="925330867@qq.com",
    description="pyxk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
