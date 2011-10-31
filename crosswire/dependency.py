"""
crosswire.dependency
============================

An extremely simple dependency injection utility.

Define it in a class like the following:

    >>> class FakeClass(object):
    ...     dep1 = dependency('Dependency')

dep1 now becomes a property to a dependency named "Dependency".
If dep1 is accessed then the dependency is resolved dynamically as follows:
    1) Locally
    2) Via crosswire
    3) Via the default

"""
from globals import dependencies

class DependencyNotFoundError(Exception):
    pass

def dependency(name, default=None):
    """A simple dependency injection utility"""
    prefix = "$"
    prefixed_name = prefix + name #To avoid infinite recursion
    def _get_dependency(self):
        local_dep = getattr(self, prefixed_name, None)
        if local_dep is not None:
            return local_dep
        dependencies_dep = getattr(dependencies, name, None)
        if dependencies_dep is not None:
            return dependencies_dep
        if default is not None:
            return default
        raise DependencyNotFoundError('Dependency named '
                '"{0}" not found'.format(name))
    def _set_dependency(self, dep):
        setattr(self, prefixed_name, dep)
    return property(_get_dependency, _set_dependency)

def get_dependency(name):
    """retrieve a dependency from the global dependencies"""
    #Check Settings
    dependencies_dep = getattr(dependencies, name, None)
    if dependencies_dep is not None:
        return dependencies_dep
    raise DependencyNotFoundError('Dependency named '
            '"{0}" not found'.format(name))

