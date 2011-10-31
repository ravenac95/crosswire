from crosswire import apply_configs, clear_config, get_dependency
from crosswire.tools import Configuration, Instance, Raw, Import
from crosswire.dependency import dependency, DependencyNotFoundError
from nose.tools import raises, assert_raises

def class_path(Cls):
    return ".".join([Cls.__module__, Cls.__name__])

class FakeClass(object):
    def __init__(self):
        self.iamfake = True

class SampleClass(object):
    dep1 = dependency("FirstDependency")
    dep2 = dependency("SecondDependency")

class SampleClassTwo(object):
    dep1 = dependency("FirstDependency", default="Hi!")

class SampleClassThree(object):
    dep1 = dependency('dep1')

def test_init_a_class_with_dependencies():
    sample = SampleClass()

@raises(DependencyNotFoundError)
def test_no_dependency_on_dep1():
    sample = SampleClass()
    dep1 = sample.dep1

@raises(DependencyNotFoundError)
def test_no_dependency_on_dep2():
    sample = SampleClass()
    dep2 = sample.dep2

def test_set_dependencies_through_apply_configs():
    class LocalConfig(Configuration):
        FirstDependency = "Hello"
        SecondDependency = "World"
    apply_configs(LocalConfig)
    sample = SampleClass()
    assert sample.dep1 == "Hello"
    assert sample.dep2 == "World"
    clear_config()

def test_set_dependency_on_one_instance_but_not_other():
    instance1 = SampleClass()
    instance2 = SampleClass()
    instance1.dep1 = "Hello"
    def test_raise_dependency_error():
        error = instance2.dep2
    assert_raises(DependencyNotFoundError, test_raise_dependency_error)
    assert instance1.dep1 == "Hello"

def test_set_dependencies_directly():
    sample = SampleClass()
    sample.dep1 = "Hello2"
    sample.dep2 = "World2"
    assert sample.dep1 == "Hello2"
    assert sample.dep2 == "World2"
    clear_config()

def test_set_dependency_directly_as_class():
    class DependencyClass(object):
        def __init__(self, test):
            self.test = test
        def get_test(self):
            return self.test

    sample = SampleClass()
    sample.dep1 = DependencyClass
    assert sample.dep1 == DependencyClass
    clear_config()

def test_set_default_dependency():
    sample = SampleClassTwo()
    assert sample.dep1 == "Hi!"
    clear_config()

def test_set_default_dependency_local_override():
    sample = SampleClassTwo()
    sample.dep1 = "Yo!"
    assert sample.dep1 == "Yo!"
    clear_config()

def test_set_default_dependency_settings_override():
    sample = SampleClassTwo()
    class LocalConfig(Configuration):
        FirstDependency = "Hola"
    apply_configs(LocalConfig)
    assert sample.dep1 == "Hola"
    clear_config()

def test_same_named_dependency():
    sample = SampleClassThree()
    sample.dep1 = "dog"
    assert sample.dep1 == "dog"

def test_dependency_instance():
    class LocalConfig(Configuration):
        FirstDependency = Instance(class_path(FakeClass))

    apply_configs(LocalConfig)
    sample = SampleClass()
    dep1 = get_dependency('FirstDependency')
    assert id(dep1) == id(sample.dep1)
    clear_config()

def test_dependency_import():
    class LocalConfig(Configuration):
        FirstDependency = Import(class_path(FakeClass))

    apply_configs(LocalConfig)
    sample = SampleClass()
    dep1 = get_dependency('FirstDependency')
    assert dep1 == FakeClass
    assert sample.dep1 == FakeClass

