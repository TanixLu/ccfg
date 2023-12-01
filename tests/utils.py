from class_config import ClassConfigBase, ClassConfigMeta


def mess_value(cls: ClassConfigMeta):
    """ 将ClassConfigBase的所有value都置为随机数 """
    import random
    config_list: list[ClassConfigMeta] = [cls]
    while config_list:
        config = config_list.pop()
        if config.is_leaf():
            old_value = config.value
            while config.value == old_value:
                config.value = random.random()
        config_list.extend(config.inner_configs())


def assert_config_dict_eq(cls: ClassConfigMeta, dct: dict):
    """ cls和某个dict等价 """
    assert cls.to_dict() == dct
    mess_value(cls)
    cls.from_dict(dct)
    assert cls.to_dict() == dct


class ComplexConfig(ClassConfigBase):
    class ParallelNum:
        name = '并行数量'
        value = 2

    class SubConfig:
        name = '子配置'

        class Speed:
            name = '速度'
            value = 3

        class Complex:
            value = {'a': [{'b': 4}, {'5': '6'}]}


complex_dict = {
    'ComplexConfig': {
        '并行数量': 2,
        '子配置': {
            '速度': 3,
            'Complex': {'a': [{'b': 4}, {'5': '6'}]}
        }
    }
}
