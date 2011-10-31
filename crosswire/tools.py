from storage import ApplicationSettingsStorage
from globals import dependencies

def apply_configs(*Configs):
    """Set new configurations (gets rid of old one)"""
    baseconfig = dict()
    for Config in Configs:
        baseconfig.update(Config.settings)
    settings = ApplicationSettingsStorage()
    settings.config(baseconfig)
    dependencies.__set_settings__(settings)

def append_configs(*Configs):
    """Append/Overwrite current configurations"""
    baseconfig = dict()
    for Config in Configs:
        baseconfig.update(Config.settings)
    settings = ApplicationSettingsStorage()
    settings.config(baseconfig)
    dependencies.__update_settings__(settings)

def default_configs(*Configs):
    """Only set if current configs have not been set"""
    baseconfig = dict()
    for Config in Configs:
        baseconfig.update(Config.settings)
    settings = ApplicationSettingsStorage()
    settings.config(baseconfig)
    dependencies.__update_defaults__(settings)

def clear_config():
    """Remove all configuration"""
    dependencies.__clear_dependencies__()

def show_configs(missing_only=False):
    settings = dependencies.__dict__['settings']
    for name, value in settings.configuration.iteritems():
        missing = False
        if value[1] is None:
            missing = True
        if not missing and missing_only:
            continue
        output = "Name: {0} - Type: {1[0]} - Value: {1[1]}".format(name, value)
        if missing:
            output = "\033[1;31m{0}\033[m".format(output)
        print output

class ConfigurationMeta(type):
    """A very simple meta class for defining application settings"""
    def __new__(cls, cls_name, bases, dct):
        """Grabs all ConfigTypes and turns them into settings.
        Other values are evaluated as raw values.
        """
        settings = dict()

        names = dct.keys()
        for name in names:
            if name.startswith('_'):
                continue
            value = dct[name]
            settings[name] = ('raw' , value)
            if isinstance(value, ConfigType):
                settings[name] = value.get_setting()
            del dct[name]
        dct['settings'] = settings
        return type.__new__(cls, cls_name, bases, dct)

class Configuration(object):
    """Class for quick configuration definitions"""
    __metaclass__ = ConfigurationMeta

class ConfigType(object):
    """Generic type for Configuration class"""
    def get_setting(self):
        return self._setting

class Raw(ConfigType):
    """Represents a raw value"""
    def __init__(self, value):
        self._setting = ("raw", value)

class Instance(ConfigType):
    """Represents a value that must be instantiated on import on resolution"""
    def __init__(self, value):
        self._setting = ("import_instance", value)

class Import(ConfigType):
    """Represents a value that must be imported on resolution"""
    def __init__(self, value):
        self._setting = ("import", value)

