# -*- coding: utf-8 -*-

"""Top-level package for nnAPEC."""

__author__ = """J. Michael Burgess"""
__email__ = 'jburgess@mpe.mpg.de'


from .utils.configuration import nnapec_config, show_configuration
from .utils.logging import (
    activate_warnings,
    silence_warnings,
    update_logging_level,
    setup_logger,
)


log = setup_logger(__name__)

from pathlib import Path

if not Path("~/.astromodels/data/nn_apec.h5").expanduser().exists():

    if not Path("~/.astromodels/data/").expanduser().exists():

        Path("~/.astromodels/data/").expanduser().mkdir(parents=True)

    log.info("copying emulator to astromodels data directory")

    from .utils.package_data import get_path_of_data_file

    import shutil

    emu_path = get_path_of_data_file("nn_apec.h5")

    astro_data_path = Path("~/.astromodels/data/nn_apec.h5").expanduser()

    shutil.copyfile(emu_path, astro_data_path)


from .nnapec import get_apec_model

from . import _version

__version__ = _version.get_versions()['version']
