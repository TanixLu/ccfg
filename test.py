from class_config import ClassConfigBase, ClassConfigMeta


def test_empty_config():
    class EmptyConfig(ClassConfigBase):
        pass

    def assert_none_meta(cls):
        assert isinstance(cls, ClassConfigMeta)
        assert cls.name is None
        assert cls.value is None

    assert_none_meta(EmptyConfig)
    assert_none_meta(EmptyConfig.asdf)
    assert_none_meta(EmptyConfig.asdf.asdf)
    assert EmptyConfig.to_dict() == {}


def assert_config_dict_eq(cls, value):
    assert cls.to_dict() == value
    cls.from_dict(value)
    assert cls.to_dict() == value


def test_config_name():
    class NoNameConfig(ClassConfigBase):
        pass

    class NamedConfig(ClassConfigBase):
        name = ''

    assert_config_dict_eq(NoNameConfig, {})
    assert_config_dict_eq(NamedConfig, {'': {}})


def test_nested_config():
    class Config(ClassConfigBase):
        class NestedConfig:
            class NestedNestedConfig:
                value = 1

        class NestedConfig2:
            value = 2

    assert_config_dict_eq(Config, {'NestedConfig': {'NestedNestedConfig': 1}, 'NestedConfig2': 2})


def test_nest_with_name():
    class Config(ClassConfigBase):
        name = 'config'

        class NestedConfig:
            name = 'nested'

            class NestedNestedConfig:
                name = 'nested_nested'
                value = 1

        class NestedConfig2:
            name = 'nested2'
            value = 2

    assert_config_dict_eq(Config, {'config': {'nested': {'nested_nested': 1}, 'nested2': 2}})
