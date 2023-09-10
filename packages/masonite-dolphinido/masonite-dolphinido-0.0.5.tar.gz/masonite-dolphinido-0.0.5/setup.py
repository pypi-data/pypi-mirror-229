from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="masonite-dolphinido",

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.0.5",
    package_dir={"": "src"},
    description="Dolphinido Audio Fingerprint and Tracking for Masonite",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project"s main homepage.
    url="https://github.com/briansimpo/masonite-dolphinido",

    # Author details
    author="Brian Simpokolwe",
    author_email="briansimpokolwe@gmail.com",

    # Choose your license
    license="MIT",

    # If your package should include things you specify in your MANIFEST.in file
    # Use this option if your package needs to include files that are not python files
    # like html templates or css files
    include_package_data=True,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",

        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Environment :: Web Environment",

        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",

        "Operating System :: OS Independent",

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",

        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",

        # List package on masonite packages
        "Framework :: Masonite",
    ],

    # What does your project relate to?
    keywords="Masonite, Python, Audio Fingerprint, Audio Tracking, SDR Radio",

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=[
        "masonitedolphinido",
        "masonitedolphinido/audiofile",
        "masonitedolphinido/commands",
        "masonitedolphinido/config",
        "masonitedolphinido/fingerprint",
        "masonitedolphinido/models",
        "masonitedolphinido/providers",
        "masonitedolphinido/radio",
        "masonitedolphinido/recognition",
        "masonitedolphinido/recorder",
    ],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip"s
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        "masonite>=4,<5",
        "attr~=0.3.2",
        "attrs~=23.1",
        "numpy~=1.25.0",
        "matplotlib~=3.7.1",
        "scipy~=1.10.1",
        "termcolor~=2.3.0",
        "pyaudio~=0.2.13",
        "pydub~=0.25.1",
        "pyrtlsdr~=0.3.0 ",
        "pyrtlsdrlib~=0.0.2",
    ]
)
