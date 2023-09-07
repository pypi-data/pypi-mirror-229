"""Orbax setup to redirect installers to checkpoint/export-specific libraries."""

import pathlib
import warnings
import setuptools

warnings.warn(
    "\n*** Orbax is a namespace, and not a standalone package. For model"
    " checkpointing and exporting utilities, please install"
    " `orbax-checkpoint` and `orbax-export` respectively (instead of"
    " `orbax`). ***\n",
    DeprecationWarning,
)

# ingest readme for pypi description
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="orbax",
    version="0.1.9",
    author="Orbax Authors",
    author_email="orbax-dev@google.com",
    description="Orbax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["orbax-checkpoint>=0.1.8"]
)
