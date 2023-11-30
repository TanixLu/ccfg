from class_config import ClassConfigBase, ClassConfigMeta


def mess_value(cls: ClassConfigMeta):
    """ 将ClassConfigBase的所有value都置为随机数 """
    import random
    config_list = [cls]
    while config_list:
        config = config_list.pop()
        if config.value is not None:
            old_value = config.value
            while config.value == old_value:
                config.value = random.random()
        config_list.extend(config.inner_configs())


def assert_config_dict_eq(cls: ClassConfigMeta, value):
    """ cls和某个dict等价 """
    assert cls.to_dict() == value
    mess_value(cls)
    cls.from_dict(value)
    assert cls.to_dict() == value


def test_empty_config():
    """
    空的config和{}等价，并且访问任意层不存在的属性，不会报错，
    而是返回一个name和value都为None的ClassConfigBase
    """

    class EmptyConfig(ClassConfigBase):
        pass

    assert_config_dict_eq(EmptyConfig, {})

    def assert_none_meta(cls):
        assert isinstance(cls, ClassConfigMeta)
        assert cls.name is None
        assert cls.value is None

    assert_none_meta(EmptyConfig)
    assert_none_meta(EmptyConfig.asdf)
    assert_none_meta(EmptyConfig.asdf.asdf)


def test_config_name():
    """ 如果最外层不设置name，那么to_dict的结果不会有最外层的name """

    class NoNameConfig(ClassConfigBase):
        pass

    class NamedConfig(ClassConfigBase):
        name = ''

    assert_config_dict_eq(NoNameConfig, {})
    assert_config_dict_eq(NamedConfig, {'': {}})


def test_inner_config():
    """ 内部配置类不用显式继承自ClassConfigBase，因为ClassConfigMeta会自动处理 """

    class Config(ClassConfigBase):
        class InnerConfig:
            class InnerInnerConfig:
                value = 1

        class InnerConfig2:
            value = 2

    assert_config_dict_eq(Config, {'InnerConfig': {'InnerInnerConfig': 1}, 'InnerConfig2': 2})


def test_nest_with_name():
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
