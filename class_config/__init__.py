import json
from pathlib import Path


class ClassConfigMeta(type):
    def __new__(cls, name, bases, attrs):
        # 创建新类
        new_class = super(ClassConfigMeta, cls).__new__(cls, name, bases, attrs)

        # 遍历字典，查找内部类并确保它们也继承自ClassConfigBase
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_'):
                if isinstance(attr_value, type):
                    # 创建一个继承自ClassConfigBase和原始内部类的新类
                    inner_class_attrs = {k: v for k, v in vars(attr_value).items()}
                    new_inner_class = type(attr_name, (ClassConfigBase, attr_value), inner_class_attrs)
                    # 将新类设置为内部类
                    setattr(new_class, attr_name, new_inner_class)

        return new_class

    def __getattr__(self, item):
        return self

    def __bool__(self):
        return False

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False


class ClassConfigBase(metaclass=ClassConfigMeta):
    name = None
    value = None

    @classmethod
    def inner_classes(cls):
        for entry in dir(cls):
            if not entry.startswith('_'):
                inner_class = getattr(cls, entry)
                # isinstance(inner_class, type)判断是否是类，等价于inspect.isclass(inner_class)
                if isinstance(inner_class, type) and issubclass(inner_class, ClassConfigBase):
                    yield inner_class

    @classmethod
    def to_dict(cls):
        # 当cls有value的时候，递归终止
        if cls.value is not None:
            return {cls.name: cls.value}

        # 否则，递归调用所有其内部类的to_json方法，合成一个大的json
        temp_json = {}
        for inner_class in cls.inner_classes():
            temp_json.update(inner_class.to_dict())

        # 如果cls有name，则给返回的结果嵌套一层dict，否则不嵌套
        if cls.name is not None:
            return {cls.name: temp_json}
        else:
            return temp_json

    @classmethod
    def from_dict(cls, j):
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
        for inner_class in cls.inner_classes():
            if inner_class.name is not None:
                if inner_class.name in j:
                    inner_class.from_dict(j)

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
