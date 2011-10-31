from werkzeug import import_string
import threading

class ApplicationDependenciesProxy(object):
    def __init__(self):
        self.__dict__['__local__'] = threading.local() #THREAD_LOCAL
        self.__dict__['settings'] = ApplicationSettingsStorage()

    def __set_settings__(self, settings):
        """Set Global Dependency Settings"""
        self.__dict__['settings'] = settings

    def __update_defaults__(self, default_settings):
        current_settings = self.__dict__.get('settings')
        if current_settings:
            current_settings.update_defaults(default_settings)
        else:
            self.__set_settings__(settings)

    def __update_settings__(self, settings):
        current_settings = self.__dict__.get('settings')
        if current_settings:
            current_settings.update(settings)
        else:
            self.__set_settings__(settings)

    def __get_local__(self):
        return self.__dict__.get("__local__")

    def __get_dependencies__(self):
        """Get the dependencies dict"""
        local = self.__get_local__()
        dependencies = getattr(local, "dependencies", None)
        if not dependencies:
            dependencies = dict()
            local.dependencies = dependencies
        return dependencies

    def __get_dependency_from_settings__(self, name):
        settings = self.__dict__['settings']
        dep = settings.get_setting(name)
        return dep

    def __getattr__(self, attr):
        dependencies = self.__get_dependencies__()
        dep = dependencies.get(attr, None)
        if not dep:
            dep = self.__get_dependency_from_settings__(attr)
            if dep: #Save for next time
                dependencies[attr] = dep
        return dep

    def __setattr__(self, attr, value):
        dependencies = self.__get_dependencies__()
        dependencies[attr] = value

    def __delattr__(self, attr):
        dependencies = self.__get_dependencies__()
        del dependencies[attr]

    def __clear_dependencies__(self):
        """Clears dependencies for all. Settings clearing is not thread safe"""
        try:
            local = self.__get_local__()
        except:
            raise Exception('Clearing dependencies failed. Please reset any'
                    ' patches before clearing dependencies')
        dependencies = dict()
        local.dependencies = dependencies
        self.__dict__['settings'] = ApplicationSettingsStorage()

class SettingsImportError(Exception):
    pass

#TODO Test application settings storage.
class ApplicationSettingsStorage(object):
    def __init__(self):
        self.configuration = dict()

    def optget_raw(self, name, value):
        return value

    def optget_import(self, name, value):
        return import_string(value)

    def optget_import_instance(self, name, value):
        try:
            Cls = import_string(value)
        except AttributeError:
            raise SettingsImportError("Unable to locate {0}".format(value))
        return Cls()

    def optget_none(self, name, value):
        return None

    def config(self, configuration):
        """
        configuration is a dict where each value is a two-tuple 
        Here's an example:
            
            {
                '[setting_name1]': ('[options]', [setting_value1]),
                '[setting_name2]': ('[options]', [setting_value2]),
            }

            options values may be:
                'raw' - Take value
                'import' - Import value from string
                'import_instance' - Import class and get instance
        """
        configuration = dict(configuration)
        self.configuration = configuration

    def get_setting(self, name):
        """Get setting from name"""
        setting = self.configuration.get(name, ('none', None))
        optget_name = str('optget_' + setting[0])
        optget_func = getattr(self, 'optget_' + setting[0])
        if setting[1] is None:
            return None
        return optget_func(setting[0], setting[1])

    def update(self, settings):
        """Updates configuration of settings.
        Overwrites any existing values"""
        update_config = settings.configuration
        self.configuration.update(update_config)

    def update_defaults(self, settings):
        """Updates configuration of settings. 
        Like update but only adds if the value isn't already set"""
        for name, value in settings.configuration.iteritems():
            current = self.configuration.get(name)
            if not current:
                self.configuration[name] = value
        

#def tester(id):
#    import random, time
#    globby.dog = []
#    for i in range(10):
#        globby.dog.append(random.choice(range(1000)))
#        print "{0}: {1}".format(id, globby.dog)
#        time.sleep(random.random())
#    q.put((id, globby.dog))
#
#q = Queue()
#if __name__ == "__main__":
#    threads = []
#    for i in range(4):
#        t = threading.Thread(target=tester, args=(i,))
#        threads.append(t)
#        t.start()
#    for t in threads:
#        t.join()
#    while not q.empty():
#        values = q.get()
#
