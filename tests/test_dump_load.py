from class_config import ClassConfigBase
from utils import ComplexConfig, complex_dict, mess_value, assert_config_dict_eq


def test_determine_form_path():
    """Test if the priority of determining format and path is correct"""

    # Priority: path parameter > form parameter > class path parameter, default is json
    class PathConfig(ClassConfigBase):
        path = "config.json"

    class NoPathConfig(ClassConfigBase):
        pass

    assert PathConfig.determine_form_path(form="toml", path="config.yml") == (
        "yml",
        "config.yml",
    )
    assert PathConfig.determine_form_path(form="toml") == ("toml", "config.toml")
    assert PathConfig.determine_form_path() == ("json", "config.json")
    assert NoPathConfig.determine_form_path() == ("json", "NoPathConfig.json")


def test_dumps_loads():
    """Test if dumps followed by loads returns the original configuration"""
    for form in ["json", "toml", "yaml"]:
        s = ComplexConfig.dumps(form)
        mess_value(ComplexConfig)
        ComplexConfig.loads(s, form)
        assert_config_dict_eq(ComplexConfig, complex_dict)
