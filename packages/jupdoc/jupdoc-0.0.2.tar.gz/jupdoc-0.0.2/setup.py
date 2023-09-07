import setuptools
import pathlib
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setuptools.setup(
     name='jupdoc',  
     version='0.0.2',
     scripts=['jupdoc/convert.py', 'jupdoc/main.py'] ,
     author="Ashish Papanai",
     author_email="ashishp@wadhwaniai.org",
     description="Convert jupyter notebooks to reports, with different levels of detail based on tags",
     long_description=README,
     long_description_content_type="text/markdown",
     url="https://github.com/wadhwaniAI/jupdoc",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=["nbconvert", "nbformat", "PyYAML", "setuptools", "coloredlogs"],
     entry_points={
        "console_scripts": [
            "jupdoc=jupdoc.__main__:main",
        ]
    },
    )