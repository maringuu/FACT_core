from __future__ import annotations

import toml
import typing
from pathlib import Path

from pydantic import BaseModel, Extra
from werkzeug.local import LocalProxy
# pylint: disable=invalid-name
_backend = None
backend: BackendConfig = LocalProxy(lambda: _backend)

_frontend = None
frontend: FrontendConfig = LocalProxy(lambda: _frontend)

_common = None
common: CommonConfig = LocalProxy(lambda: _common)


class _PydanticConfigExtraForbid:
    # FIXME this should be replaced by class kwargs (extra=Extra.forbid)
    # Sphinx autodoc will complain about unknown kwargs
    extra = Extra.forbid


class _PydanticConfigExtraAllow:
    extra = Extra.allow


class _Redis(BaseModel):
    Config = _PydanticConfigExtraForbid

    fact_db: str
    test_db: str
    host: str
    port: int


class _Postgres(BaseModel):
    Config = _PydanticConfigExtraForbid

    server: str
    port: int
    database: str
    test_database: str

    ro_user: str
    ro_pw: str

    rw_user: str
    rw_pw: str

    del_user: str
    del_pw: str

    admin_user: str
    admin_pw: str


class _UserStore(BaseModel):
    Config = _PydanticConfigExtraForbid

    user_database: str
    password_salt: str


class _Logging(BaseModel):
    Config = _PydanticConfigExtraForbid

    level: str
    file: str


class CommonConfig(BaseModel):
    Config = _PydanticConfigExtraForbid

    redis: _Redis
    logging: _Logging

    def _verify(self):
        pass


class FrontendConfig(BaseModel):
    Config = _PydanticConfigExtraForbid

    results_per_page: int
    number_of_latest_firmwares_to_display: int = 10
    ajax_stats_reload_time: int

    max_elements_per_chart: int = 10

    # Das sollte die ganze url sein, damit man nginx weglassen kann.
    radare2_host: str

    def _verify(self):
        pass


class _Unpacking(BaseModel):
    processes: int
    whitelist: list
    max_depth: int
    memory_limit: int = 2048

    threshold: float
    throttle_limit: int


class _Plugin(BaseModel):
    Config = _PydanticConfigExtraAllow

    name: str


class _Preset(BaseModel):
    Config = _PydanticConfigExtraForbid

    name: str
    plugins: list[str]


class BackendConfig(BaseModel):
    Config = _PydanticConfigExtraForbid

    postgres: _Postgres
    unpacking: _Unpacking
    userstore: _UserStore

    firmware_file_storage_directory: str
    temp_dir_path: str = '/tmp'
    docker_mount_base_dir: str

    authentication: bool

    block_delay: float
    ssdeep_ignore: int

    communication_timeout: int = 60

    intercom_poll_delay: float

    throw_exceptions: bool

    plugin: typing.Dict[str, _Plugin]
    # TODO this does not work
    presets: typing.Dict[str, _Preset]

    def _verify(self):
        if not Path(self.temp_dir_path).exists():
            raise ValueError('The "temp-dir-path" does not exist.')


def load(path: str | None = None):
    # pylint: disable=global-statement
    """Load the config file located at ``path``.
    The file must be a toml file and is read into instances of :py:class:`~config.BackendConfig`,
    :py:class:`~config.FrontendConfig` and :py:class:`~config.CommonConfig`.

    These instances can be accessed via ``config.backend`` after calling this function.

    .. important::
        This function may not be imported by ``from config import load``.
        It may only be imported by ``import config`` and then used by ``config.load()``.
        The reason is that testing code can't patch this function if it was already imported.
        When you only import the ``config`` module the ``load`` function will be looked up at runtime.
        See `this blog entry <https://alexmarandon.com/articles/python_mock_gotchas/>`_ for some more information.
    """
    if path is None:
        path = Path(__file__).parent / 'config/fact-core.toml.example'

    with open(path, encoding='utf8') as f:
        cfg = toml.load(f)

    _replace_hyphens_with_underscores(cfg)

    backend_dict = cfg["backend"]

    presets_list = backend_dict.pop("presets", [])
    presets_dict = dict()
    for preset in presets_list:
        p = _Preset(**preset)
        presets_dict[p.name] = p

    backend_dict["presets"] = presets_dict

    plugin_list = backend_dict.pop("plugin", [])
    plugin_dict = dict()
    for plugin in plugin_list:
        p = _Plugin(**plugin)
        plugin_dict[p.name] = p

    backend_dict["plugin"] = plugin_dict

    global _backend
    if "backend" in cfg:
        _backend = BackendConfig(**cfg["backend"])
        _backend._verify()

    global _frontend
    if "frontend" in cfg:
        _frontend = FrontendConfig(**cfg["frontend"])
        _frontend._verify()

    global _common
    _common = CommonConfig(**cfg["common"])
    _common._verify()


def _replace_hyphens_with_underscores(dictionary):
    if not isinstance(dictionary, dict):
        return

    for key in list(dictionary.keys()):
        _replace_hyphens_with_underscores(dictionary[key])
        value = dictionary.pop(key)
        dictionary[key.replace('-', '_')] = value
