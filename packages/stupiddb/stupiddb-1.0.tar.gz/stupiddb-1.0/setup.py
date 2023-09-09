from setuptools import setup

setup (
    name="stupiddb", 
    version="1.0", 
    description="The stupidest database system ever made",
    long_description= open("README.md").read(),
    long_description_content_type= "text/markdown",
    project_urls={"GitHub Repository": "https://github.com/gugu256/StupidDB"},
    author="gugu256",
    author_email="gugu256@mail.com",
    url="https://github.com/gugu256",
    keywords="database key value key-value KV esoteric",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)