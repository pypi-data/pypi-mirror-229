from setuptools import setup, find_packages

setup(
    name="blackfalcon",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # 여기에 필요한 종속성을 나열합니다. 
    ],
    author="BlackFlacon",
    description="A macro package for blackfalcon",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SpeeDr00t",
)

