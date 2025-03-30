import os
from typing import Optional, Any, Tuple
from pathlib import Path


class CcfgMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        # Add kwargs to attrs
        attrs.update(kwargs)

        # Iterate through attrs, find inner classes and ensure they also inherit from CCFG
        # This way when using CCFG, inner classes don't need to explicitly inherit from CCFG
        inner_class_names = set()
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith("_"):
                if isinstance(attr_value, type):
                    # Create a new class that inherits from CCFG and the original inner class
                    inner_class_attrs = {k: v for k, v in vars(attr_value).items()}
                    new_inner_class = type(
                        attr_name, (CCFG, attr_value), inner_class_attrs
                    )
                    # Replace the original inner class with the new class
                    attrs[attr_name] = new_inner_class
                    # Record the inner class name, inner class names cannot be duplicated
                    inner_class_name = (
                        attr_value.name if hasattr(attr_value, "name") else attr_name
                    )
                    if inner_class_name in inner_class_names:
                        raise ValueError(
                            f'Inner class name "{inner_class_name}" is duplicated'
                        )
                    inner_class_names.add(inner_class_name)

        # If there's no name in attrs, set name to the class name
        if "name" not in attrs:
            attrs["name"] = name

        return super().__new__(cls, name, bases, attrs)

    def __getattr__(cls, item):
        return CCFG

    def __bool__(cls):
        return False

    def __eq__(cls, other):
        return False

    def __ne__(cls, other):
        return False


class CCFG(metaclass=CcfgMeta):
    """
    class Config(CCFG):
        class ParallelNum:
            name = 'Parallel Count'

            value = 2

        class SubConfig:
            name = 'Sub Configuration'

            class Speed:
                name = 'Speed'

                value = 3

            class Complex:  # The default name is the class name
                value = {'4': ['5', {'6': 7}]}

    assert Config.to_dict() == {'Config': {'Parallel Count': 2, 'Sub Configuration': {'Speed': 3, 'Complex': {'4': ['5', {'6': 7}]}}}}

    Attributes:
        name: Corresponds to the dict key, defaults to class name.
        value: Corresponds to the dict value. When there are inner configs, they take precedence, and the value becomes a dict composed of all inner config key-value pairs.
    """

    name: str = None  # type: ignore
    value: Any = None  # type: ignore

    @classmethod
    def inner_configs(cls):
        """
        Return all internal classes that inherit from CCFG. Since CcfgMeta handles this automatically,
        these classes may not explicitly inherit from CCFG.
        """
        for entry in dir(cls):
            if not entry.startswith("_"):
                inner_class = getattr(cls, entry)
                # isinstance(inner_class, type) checks if it's a class, equivalent to inspect.isclass(inner_class)
                if isinstance(inner_class, type) and issubclass(inner_class, CCFG):
                    yield inner_class

    @classmethod
    def is_leaf(cls):
        """A leaf configuration is one without inner configs"""
        return all(False for _ in cls.inner_configs())

    @classmethod
    def to_dict(cls):
        """Convert the configuration to dict"""
        # If it's a leaf node, return value directly
        if cls.is_leaf():
            return {cls.name: cls.value}

        # Otherwise, recursively call the to_dict method
        dict_value = {}
        for inner_config in cls.inner_configs():
            dict_value.update(inner_config.to_dict())

        return {cls.name: dict_value}

    @classmethod
    def from_dict(cls, dct: dict):
        """Convert dict to configuration"""
        if cls.name in dct:
            dct = dct[cls.name]
            if cls.is_leaf():
                # If it's a leaf node, terminate recursion and set the value directly
                cls.value = dct
            elif isinstance(dct, dict):
                # For non-leaf nodes, iterate through inner configs and make recursive calls
                for inner_config in cls.inner_configs():
                    if inner_config.name in dct:
                        inner_config.from_dict(dct)

    @classmethod
    def dumps(cls, form: str, **kwargs):
        """Convert configuration to str, supported formats include json, toml, yaml, default is json"""
        dct = cls.to_dict()
        if form == "toml":
            import toml

            return toml.dumps(dct, **kwargs)
        elif form == "yaml" or form == "yml":
            import yaml

            return yaml.dump(dct, **kwargs)
        else:
            import json

            # Set default json dumps parameters to make the output format more readable
            kwargs.setdefault("ensure_ascii", False)
            kwargs.setdefault("indent", 2)
            return json.dumps(dct, **kwargs)

    @classmethod
    def loads(cls, s: str, form: str, **kwargs):
        """Convert str to configuration, supported formats include json, toml, yaml, default is json"""
        if form == "toml":
            import toml

            dct = toml.loads(s, **kwargs)
        elif form == "yaml" or form == "yml":
            import yaml

            dct = yaml.safe_load(s)
        else:
            import json

            dct = json.loads(s, **kwargs)

        cls.from_dict(dct)

    @classmethod
    def determine_form_path(
        cls, form: Optional[str] = None, path: Optional[str] = None
    ) -> Tuple[str, str]:
        """Determine format and path"""
        # First determine the format, priority: path parameter > form parameter > class path parameter, default is json
        if path is not None:
            form = path.rsplit(".", 1)[-1]
        elif form is None:
            if isinstance(cls.path, str):
                form = cls.path.rsplit(".", 1)[-1]
            else:
                form = "json"

        # Determine file name, priority: path parameter > class path parameter > class name
        if path is not None:
            file_name = path.rsplit(".", 1)[0]
        else:
            if isinstance(cls.path, str):
                file_name = cls.path.rsplit(".", 1)[0]
            else:
                file_name = cls.name

        # Combine file name and extension to get the path
        # Note that the default extension for yaml format is yml
        if form == "yaml":
            ext = "yml"
        else:
            ext = form
        path = file_name + "." + ext

        return form, path

    @classmethod
    def load(
        cls, form: Optional[str] = None, path: Optional[str] = None, **kwargs
    ) -> bool:
        """Load configuration from file, supported formats include json, toml, yaml, default is json"""
        final_form, final_path = cls.determine_form_path(form, path)
        if os.path.exists(final_path):
            with open(final_path, "r", encoding="utf-8") as f:
                cls.loads(f.read(), final_form, **kwargs)
            return True
        else:
            return False

    @classmethod
    def dump(cls, form: Optional[str] = None, path: Optional[str] = None, **kwargs):
        """Save configuration to file, supported formats include json, toml, yaml, default is json"""
        final_form, final_path = cls.determine_form_path(form, path)

        Path(final_path).parent.mkdir(parents=True, exist_ok=True)

        with open(final_path, "w", encoding="utf-8") as f:
            f.write(cls.dumps(final_form, **kwargs))
