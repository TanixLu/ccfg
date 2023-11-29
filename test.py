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


def assert_config_json_eq(cls, value):
    assert cls.to_dict() == value
    cls.from_dict(value)
    assert cls.to_dict() == value


def test_config_name():
    class NoNameConfig(ClassConfigBase):
        pass

    class NamedConfig(ClassConfigBase):
        name = ''

    assert_config_json_eq(NoNameConfig, {})
    assert_config_json_eq(NamedConfig, {'': {}})


def test_nested_config():
    class NestedConfig(ClassConfigBase):

        class Config1:
            value = 1

    print(NestedConfig.to_dict())
