import setuptools
# used by python -m build
# python -m build needs pyproject.toml or setup.py
setuptools.setup(
     name='entity-type-local',
     version='0.0.12',
     author="Circles",
     author_email="info@circles.life",
     description="PyPI Package for Circles Local Entity Type Python (Currently empty package)",
     long_description="This is a package for sharing common importer function used in different repositories",
     long_description_content_type="text/markdown",
     url="https://github.com/javatechy/dokr",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: Other/Proprietary License",
         "Operating System :: OS Independent",
     ],
 )
