from setuptools import setup, find_packages

setup(
    name="MingLogCVUtils",
    version="1.0.1",
    packages=find_packages(),
    py_modules=["CVUtils"],
    install_requires=[
        'numpy',
        'matplotlib',
        'pillow',
        'opencv-python',
        'aiofiles',
        'scipy'
    ],
    include_package_data=True,
    author="MingLog",
    author_email="736704198@qq.com",
    description="计算机识别工具库",
    long_description=open("README.md", encoding='UTF-8').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://minglog.hzbmmc.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)