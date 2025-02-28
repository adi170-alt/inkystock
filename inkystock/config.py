import os
from configparser import ConfigParser
from typing import List, Optional

from pydantic import BaseModel, validator, HttpUrl


class ConfigurationException(ValueError):
    """Configuration Exception"""


class MainConfig(BaseModel):
    currency = "EUR"
    database = "sqlite:////tmp/inkystock.db"
    stock: str = ""
    crypto: str = "BTC"
    provider: str
    display_width_pixels: int = 212
    display_height_pixels: int = 104
    display_diagonal_inches: float = 2.13
    rotate_display: int = 0
    loglevel: str = "INFO"

    @validator('currency')
    def currency_is_upper(cls, v):
        if not v.isupper():
            raise ConfigurationException("must be uppercase")
        return v

    @validator('stock')
    def only_stock_set(cls, v, values, **kwargs):
        if len(v) and len(values.get('crypto', "")):
            raise ConfigurationException('One of *either* stock or crypto must be specified')
        return v

    @validator('crypto')
    def only_crypto_set(cls, v, values, **kwargs):
        if len(v) and len(values.get('stock', "")):
            raise ConfigurationException("One of *either* stock or crypto must be specified")
        return v

    @validator('loglevel')
    def valid_loglevel(cls, v):
        loglevels = ['NOTSET', 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        if not v.isupper():
            raise ConfigurationException("must be uppercase")
        if v not in loglevels:
            raise ConfigurationException(f"loglevel must be one of {loglevels}")
        return v


class FontsConfig(BaseModel):
    ticker: str = "./resources/fonts/04B_03__.TTF"
    ticker_size: int = 8
    symbol: str = "./resources/fonts/04B_21__.TTF"
    symbol_size: int = 10
    statusbar: str = "./resources/fonts/CozetteVector.ttf"
    statusbar_size: int = 12
    headline: str = "./resources/fonts/04B_30__.TTF"
    headline_size: int = 30
    chart: str = "./resources/fonts/04B_03__.TTF"
    chart_size: float = 5.2


class MascotConfig(BaseModel):
    increasing: str = "./resources/pixelcat/pixelcat_cool.png"
    decreasing: str = "./resources/pixelcat/pixelcat_worried.png"
    static: str = "./resources/pixelcat/pixelcat_sleeping.png"


class IEXConfig(BaseModel):
    token: str
    endpoint: HttpUrl = "https://cloud.iexapis.com/stable"


class OutputConfig(BaseModel):
    screen: str = "inky"
    local: str = "./data/out.png"


class Config:

    def __init__(self, env_vars: Optional[List] = None, path: str = 'config.ini'):
        """
        Read configuration file and set map to Pydantic models.
        :param path: path to the configuration file
        :param: env: environment dictionary
        :return: a Config object
        :rtype: Config
        """
        # Populate the config with environment variables
        env = {}
        if env_vars is None:
            env_vars = []
        for env_var in env_vars:
            if os.getenv(env_var):
                env[env_var] = str(os.getenv(env_var))

        self.__config = ConfigParser(env)
        self.__config.read(path)

        self.main = MainConfig(**self.__config['Main'])
        self.outputs = OutputConfig()
        if self.__config.has_section('Outputs'):
            self.outputs = OutputConfig(**self.__config['Outputs'])
        self.fonts = FontsConfig(**self.__config['Fonts'])
        self.mascot = MascotConfig(**self.__config['Mascot'])

        # IEXCloud provider configuration
        self.iex = IEXConfig(token="")
        if self.main.provider == 'IEX':
            self.iex = IEXConfig(**self.__config['IEX'])
