from src.ccfg import CCFG, CcfgMeta
from utils import assert_config_dict_eq


def test_empty_config():
    """
    An empty config is equivalent to {'ConfigName': None}, and accessing any non-existent attribute
    at any level will not raise an error, but rather return a CCFG with name and value
    both set to None
    """

    class EmptyConfig(CCFG):
        pass

    assert EmptyConfig.name == "EmptyConfig"
    assert EmptyConfig.value is None

    assert_config_dict_eq(EmptyConfig, {"EmptyConfig": None})

    def assert_none_meta(cls):
        assert isinstance(cls, CcfgMeta)
        assert cls.name is None
        assert cls.value is None

    assert_none_meta(EmptyConfig.asdf)
    assert_none_meta(EmptyConfig.asdf.asdf)


def test_inner_config():
    """Inner configuration classes don't need to explicitly inherit from CCFG because CcfgMeta handles it automatically"""

    class Config(CCFG):
        class InnerConfig:
            class InnerInnerConfig:
                value = 1

        class InnerConfig2:
            value = 2

    assert_config_dict_eq(
        Config, {"Config": {"InnerConfig": {"InnerInnerConfig": 1}, "InnerConfig2": 2}}
    )


def test_inner_with_name():
    """Mix of inner configuration classes and explicit name"""

    class Config(CCFG):
        name = "config"

        class InnerConfig:
            name = "asdf"

            class InnerInnerConfig:
                value = 1

        class InnerConfig2:
            name = "inner2"
            value = 2

    assert_config_dict_eq(
        Config, {"config": {"asdf": {"InnerInnerConfig": 1}, "inner2": 2}}
    )


def test_none_name():
    """name can be None"""

    class NoneNameConfig(CCFG):
        name = None
        value = 3

    assert_config_dict_eq(NoneNameConfig, {None: 3})


def test_duplicate_name():
    """Cannot have duplicate names"""
    try:
        # Both set the same name
        class _Config(CCFG):
            class InnerConfig:
                name = "asdf"

            class InnerConfig2:
                name = "asdf"

        assert False
    except ValueError:
        pass

    try:
        # One sets name, one uses default
        class _Config(CCFG):
            class InnerConfig:
                pass

            class InnerConfig2:
                name = "InnerConfig"

        assert False
    except ValueError:
        pass

    try:
        # Both set name to None
        class _Config(CCFG):
            class InnerConfig:
                name = None

            class InnerConfig2:
                name = None

        assert False
    except ValueError:
        pass


def test_complex_config():
    """Test complex configuration"""
    from utils import ComplexConfig, complex_dict

    assert_config_dict_eq(ComplexConfig, complex_dict)
