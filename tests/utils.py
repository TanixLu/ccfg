from src.ccfg import CCFG


def mess_value(cls: CCFG):
    """Set all values of CCFG to random numbers"""
    import random

    config_list: list[CCFG] = [cls]
    while config_list:
        config = config_list.pop()
        if config.is_leaf():
            old_value = config.value
            while config.value == old_value:
                config.value = random.random()
        config_list.extend(config.inner_configs())


def assert_config_dict_eq(cls: CCFG, dct: dict):
    """Verify that cls is equivalent to a specified dict"""
    assert cls.to_dict() == dct
    mess_value(cls)
    cls.from_dict(dct)
    assert cls.to_dict() == dct


class ComplexConfig(CCFG):
    class ParallelNum:
        name = "Parallel Count"
        value = 2

    class SubConfig:
        name = "Sub Configuration"

        class Speed:
            name = "Speed"
            value = 3

        class Complex:
            value = {"a": [{"b": 4}, {"5": "6"}]}


complex_dict = {
    "ComplexConfig": {
        "Parallel Count": 2,
        "Sub Configuration": {"Speed": 3, "Complex": {"a": [{"b": 4}, {"5": "6"}]}},
    }
}
