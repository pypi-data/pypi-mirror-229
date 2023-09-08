from setuptools import setup

with open("README.rst") as fh:
    readme = fh.read()

setup(
    name="galaxyxmlfubar",
    version="0.4.16",
    description="Galaxy XML generation library fork",
    author="Ross Lazarus",
    author_email="oldf4rt@hotmail.com",
    install_requires=["lxml", "galaxy-tool-util"],
    long_description=readme,
    long_description_content_type="text/x-rst",
    packages=["galaxyxmlfubar", "galaxyxmlfubar.tool", "galaxyxmlfubar.tool.parameters"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
    ],
    data_files=[("", ["LICENSE.TXT"])]
)
