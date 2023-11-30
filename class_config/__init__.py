import json
from pathlib import Path


class ClassConfigMeta(type):
    _depth = 0

    def __new__(cls, name, bases, attrs, **kwargs):
        ClassConfigMeta._depth += 1

        if ClassConfigMeta._depth == 1 and name != 'ClassConfigBase':
            # _depth为1，代表这是最顶层的Config，因此设置_outermost为True
            # name != 'ClassConfigBase'，代表这不是ClassConfigBase本身
            attrs['_outermost'] = True

        # 将kwargs加入attrs
        attrs.update(kwargs)

        # 遍历attrs，查找inner class并确保它们也继承自ClassConfigBase
        # 这样在使用ClassConfigBase的时候，inner class就不用显式地继承自ClassConfigBase了
        inner_class_names = set()
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_'):
                if isinstance(attr_value, type):
                    # 创建一个继承自ClassConfigBase和原始内部类的新类
                    inner_class_attrs = {k: v for k, v in vars(attr_value).items()}
                    new_inner_class = type(attr_name, (ClassConfigBase, attr_value), inner_class_attrs)
                    # 将原始内部类替换为新类
                    attrs[attr_name] = new_inner_class
                    # 记录内部类的名字，内部类的名字不能重复
                    inner_class_name = attr_value.name if hasattr(attr_value, 'name') else attr_name
                    if inner_class_name in inner_class_names:
                        raise ValueError(f'Inner class name "{inner_class_name}" is duplicated')
                    inner_class_names.add(inner_class_name)

        # inner class和value不能同时存在
        if inner_class_names and 'value' in attrs and attrs['value'] is not None:
            raise ValueError('Inner class and value cannot both exist')

        # 如果attrs中没有name，则将name设置为类名（最顶层的Config除外）
        if ClassConfigMeta._depth != 1 and 'name' not in attrs:
            attrs['name'] = name

        ClassConfigMeta._depth -= 1

        return super().__new__(cls, name, bases, attrs)

    def __getattr__(cls, item):
        return ClassConfigBase

    def __bool__(cls):
        return False

    def __eq__(cls, other):
        return False

    def __ne__(cls, other):
        return False


class ClassConfigBase(metaclass=ClassConfigMeta):
    """
    class Config(ClassConfigBase):
        class ParallelNum:
            name = '并行数量'

            value = 2

        class SubConfig:
            name = '子配置'

            class Speed:
                name = '速度'

                value = 3

            class Complex:  # 默认name为类名
                value = {'4': ['5', {'6': 7}]}

    assert Config.to_dict() == {'并行数量': 2, '子配置': {'速度': 3, 'Complex': {'4': ['5', {'6': 7}]}}}

    Attributes:
        name: 总是存在，默认为类名。只有最顶层的Config为None时，才不显示name。
        value: 总是存在，但是当有inner config时，value必须为None。
    """

    name = None
    value = None

    @classmethod
    def inner_configs(cls):
        """
        返回所有内部继承自ClassConfigBase的类，由于ClassConfigMeta会自动处理，
        因此这些类不一定显式继承自ClassConfigBase。
        """
        for entry in dir(cls):
            if not entry.startswith('_'):
                inner_class = getattr(cls, entry)
                # isinstance(inner_class, type)判断是否是类，等价于inspect.isclass(inner_class)
                if isinstance(inner_class, type) and issubclass(inner_class, ClassConfigBase):
                    yield inner_class

    @classmethod
    def to_dict(cls):
        """ 将配置转换为dict """

        # 当cls有value的时候，递归终止
        if cls.value is not None:
            return {cls.name: cls.value}

        # 否则，递归调用所有其内部类的to_json方法，合成一个大的json
        res_dict = {}
        for inner_config in cls.inner_configs():
            res_dict.update(inner_config.to_dict())

        # 如果cls在最外层，且name为None，不显示name
        if hasattr(cls, '_outermost') and cls._outermost and cls.name is None:
            return res_dict
        else:
            return {cls.name: res_dict}

    @classmethod
    def from_dict(cls, j):
        """ 将dict转换为配置 """

        # 当cls有value的时候，递归终止
        if cls.value is not None:
            if cls.name in j:
                cls.value = j[cls.name]
                return

        # 否则，尝试去掉一层j的嵌套
        if cls.name is not None:
            if cls.name in j:
                j = j[cls.name]

        # 然后对于其所有内部类，递归调用from_json方法
        for inner_config in cls.inner_configs():
            if inner_config.name is not None:
                if inner_config.name in j:
                    inner_config.from_dict(j)

    @classmethod
    def write_json(cls, file_path):
        with open(file_path, 'w', encoding='utf8') as f:
            json.dump(cls.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def read_json(cls, file_path):
        path = Path(file_path)
        if path.exists() and path.stat().st_size > 0:
            with open(path, encoding='utf8') as f:
                cls.from_dict(json.load(f))
        else:
            cls.write_json(file_path)
