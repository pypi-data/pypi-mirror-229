import yaml
import pathlib
import logging
import typing
import os

from . import models

logger = logging.getLogger(__name__)

try:
    import np_config
    USING_NP_CONFIG = True
except ImportError:
    logger.error("Error importing np_config.", exc_info=True)
    USING_NP_CONFIG = False


DEFAULT_FILE_CONFIG_DEV = r"\\allen\programs\mindscope\workgroups\dynamicrouting\chrism\mtrain-superclient-recipies\dev\dynamicrouting.yml"
DEFAULT_FILE_CONFIG_PROD = r"\\allen\programs\mindscope\workgroups\dynamicrouting\chrism\mtrain-superclient-recipies\prod\dynamicrouting.yml"
DEFAULT_NP_CONFIG_DEV = "mtrain-superclient/dev"
DEFAULT_NP_CONFIG_PROD = "mtrain-superclient/prod"


def resolve_config_path(name: str, default: str) -> str:
    try:
        path = os.environ[name]
        logger.debug("Environment override present: %s=%s" % (name, path))
        return path
    except KeyError:
        logger.debug("Using default: %s=%s" % (name, default))
        return default


def from_file(config_file: pathlib.Path) -> models.RegimenUpdateRecipie:
    return models.RegimenUpdateRecipie.from_dict(
        yaml.safe_load(config_file.read_text())
    )


def from_np_config(np_config_name: str) -> models.RegimenUpdateRecipie:
    try:
        resolved = np_config.from_zk(np_config_name)
        return models.RegimenUpdateRecipie.from_dict(resolved)
    except Exception as e:
        logger.error("Error loading np_config. np_config_name=%s" % np_config_name)


def get(use_prod: False) -> models.RegimenUpdateRecipie:
    # TODO: actually use np-config
    if use_prod:
        resolved_path = resolve_config_path(
            "FILE_CONFIG_PATH",
            DEFAULT_FILE_CONFIG_PROD,
        )
    else:
        resolved_path = resolve_config_path(
            "FILE_CONFIG_PATH",
            DEFAULT_FILE_CONFIG_DEV,
        )
    resolved = from_file(pathlib.Path(resolved_path))
    logger.debug("Resolved config: %s" % resolved)
    return resolved