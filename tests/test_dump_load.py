from class_config import ClassConfigBase
from utils import ComplexConfig, complex_dict, mess_value, assert_config_dict_eq


def test_determine_form_path():
    """测试确定格式以及路径的优先级是否正确"""

    # 优先级：path参数 > form参数 > 类path参数，默认为json
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
    """测试dumps后loads，是否得到原来的配置"""
    for form in ["json", "toml", "yaml"]:
        s = ComplexConfig.dumps(form)
        mess_value(ComplexConfig)
        ComplexConfig.loads(s, form)
        assert_config_dict_eq(ComplexConfig, complex_dict)
