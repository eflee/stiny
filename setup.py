from setuptools import setup, find_packages

setup(
    name="stiny",
    version="1.0",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    scripts=['bin/stiny'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3', 'boto>=2.32', 'docopt>=0.6', 'jinja2>=2.7', 'voluptuous>=0.8.5'],

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
    url="http://elif.us/stiny",  # project home page, if any
    test_suite='test',

    # could also include long_description, download_url, classifiers, etc.
)
