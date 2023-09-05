import setuptools

setuptools.setup(
    name='logger-local',
    version='0.0.54',  # https://pypi.org/project/logger-local/
    author="Circles",
    author_email="info@circles.life",
    description="PyPI Package for Circles Logger Python Local",
    long_description="This is a package for sharing common Logger function used in different repositories",
    long_description_content_type="text/markdown",
    url="https://github.com/circles-zone/logger-local-python-package",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
