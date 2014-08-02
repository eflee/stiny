from setuptools import setup, find_packages

setup(
    name="stiny",
    version="0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=[],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3', 'boto', 'docopt', 'jinja2'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst']
    },

    # metadata for upload to PyPI
    author="Eli Flesher",
    author_email="eli@eflee.us",
    description="A Command-line Tiny Link solution for static backing stores",
    license="Apache",
    keywords="s3 gcs tinyurl static",
    url="http://eflee.us/tinyurl",  # project home page, if any
    test_suite='test',

    # could also include long_description, download_url, classifiers, etc.
)
