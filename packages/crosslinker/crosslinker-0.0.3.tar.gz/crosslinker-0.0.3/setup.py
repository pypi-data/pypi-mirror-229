from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='crosslinker',
    version='0.0.3',
    description="CrossLinker: A Python Library for SEO - Friendly HTML Text Processing and Keyword Linking",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Mark',
    author_email='markolofsen@gmail.com',
    url='https://github.com/markolofsen/crosslinker',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'nltk',
    ],
    # package_dir={'': 'py-seo-html'},
    py_modules=['crosslinker'],
)
