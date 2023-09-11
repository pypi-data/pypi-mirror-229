import setuptools
# used by python -m build
# python -m build needs pyproject.toml or setup.py
setuptools.setup(
    # TODO: Please update the name
    name='location-local',
    version='0.0.24',  # https://pypi.org/project/location-local/
    author="Circles",
    author_email="info@circles.life",
    description="Location Locatal PyPI Package",
    long_description="This is a package for sharing common OpenCage function used in different repositories",
    long_description_content_type="text/markdown",
    url="https://github.com/javatechy/dokr",
    packages=setuptools.find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
    ],
)
