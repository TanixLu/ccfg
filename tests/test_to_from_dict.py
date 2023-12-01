from class_config import ClassConfigBase, ClassConfigMeta
from utils import assert_config_dict_eq


def test_empty_config():
    """
    空的config和{'ConfigName': None}等价，并且访问任意层不存在的属性，不会报错，
    而是返回一个name和value都为None的ClassConfigBase
    """

    class EmptyConfig(ClassConfigBase):
        pass

    assert EmptyConfig.name == 'EmptyConfig'
    assert EmptyConfig.value is None

    assert_config_dict_eq(EmptyConfig, {'EmptyConfig': None})

    def assert_none_meta(cls):
        assert isinstance(cls, ClassConfigMeta)
        assert cls.name is None
        assert cls.value is None

    assert_none_meta(EmptyConfig.asdf)
    assert_none_meta(EmptyConfig.asdf.asdf)


def test_inner_config():
    """ 内部配置类不用显式继承自ClassConfigBase，因为ClassConfigMeta会自动处理 """

    class Config(ClassConfigBase):
        class InnerConfig:
            class InnerInnerConfig:
                value = 1

        class InnerConfig2:
            value = 2

    assert_config_dict_eq(Config, {'Config': {'InnerConfig': {'InnerInnerConfig': 1}, 'InnerConfig2': 2}})


def test_inner_with_name():
    """ 内部配置类和显式name混用 """

    class Config(ClassConfigBase):
        name = 'config'

        class InnerConfig:
            name = 'asdf'

            class InnerInnerConfig:
                value = 1

        class InnerConfig2:
            name = 'inner2'
            value = 2

    assert_config_dict_eq(Config, {'config': {'asdf': {'InnerInnerConfig': 1}, 'inner2': 2}})


def test_none_name():
    """ name可以是None """

    class NoneNameConfig(ClassConfigBase):
        name = None
        value = 3

    assert_config_dict_eq(NoneNameConfig, {None: 3})


def test_duplicate_name():
    """ 不能有重复的name """
    try:
        # 两个都设置name
        class _Config(ClassConfigBase):
            class InnerConfig:
                name = 'asdf'

            class InnerConfig2:
                name = 'asdf'

        assert False
    except ValueError:
        pass

    try:
        # 一个设置name，一个不设置
        class _Config(ClassConfigBase):
            class InnerConfig:
                pass

            class InnerConfig2:
                name = 'InnerConfig'

        assert False
    except ValueError:
        pass

    try:
        # 两个都设置name为None
        class _Config(ClassConfigBase):
            class InnerConfig:
                name = None

            class InnerConfig2:
                name = None

        assert False
    except ValueError:
        pass


def test_complex_config():
    """ 测试复杂配置 """
    from utils import ComplexConfig, complex_dict
    assert_config_dict_eq(ComplexConfig, complex_dict)
