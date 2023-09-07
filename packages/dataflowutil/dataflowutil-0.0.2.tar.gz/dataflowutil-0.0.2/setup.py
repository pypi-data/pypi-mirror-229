from setuptools import setup

setup(
    name = "dataflowutil",
    version = "0.0.2",
    author="Felipe Ardila (WorldArd)",
    description="",
    include_package_data=True,
    packages=["dataflowutil.config","dataflowutil.libs"],
    install_requires = [
        "pandas==1.5.0",
        "pandas-gbq==0.19.2",
        "google-cloud-storage==2.10.0",
        "openpyxl==3.1.2",
        "fsspec==2023.6.0",
        "gcsfs==2023.6.0",
    ],
)