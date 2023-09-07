import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timeskorch",
    version="0.0.1",
    author="mingukang",
    author_email="kang.mingu94@gmail.com",
    description="Time Skorch (TS) is a powerful tool designed to make time series analysis and forecasting a breeze.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minqukanq/timeskorch",
    install_requires=['scikit-learn', 'skorch'],
    packages=setuptools.find_packages(),
    keywords=['time series', 'sklearn', 'pytorch', 'skorch', 'deep learning'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
