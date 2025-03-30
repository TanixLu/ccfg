# class_config

A Python library for managing hierarchical configurations using a class-based approach.

## Features

- Define configuration hierarchies using Python classes
- Automatically convert between configuration classes and dictionaries
- Support for multiple serialization formats (JSON, TOML, YAML)
- Simple file-based storage and retrieval

## Installation

```bash
pip install class_config
```

## Usage Example

Below is a comprehensive example demonstrating the main features:

```python
from class_config import ClassConfigBase

class ApplicationConfig(ClassConfigBase):
    # Custom path for file storage
    path = "configs/app_settings.json"

    # No explicit name, will use class name "ApplicationConfig" as default

    class Database:
        # Custom name for this section
        name = "DatabaseSettings"

        class Connection:
            # No explicit name, will use "Connection" by default
            value = "postgresql://user:password@localhost:5432/mydb"

        class Pooling:
            name = "ConnectionPool"
            value = {"max_connections": 10, "timeout": 30}

    class Logging:
        # Using default name "Logging"

        class Level:
            value = "INFO"

        class Output:
            name = "OutputPath"
            value = "/var/log/app.log"

    class Features:
        # Using a list for complex values
        value = ["authentication", "api", "admin_panel"]


# Convert to dictionary
config_dict = ApplicationConfig.to_dict()
print(config_dict)
# Output:
# {
#   "ApplicationConfig": {
#     "DatabaseSettings": {
#       "Connection": "postgresql://user:password@localhost:5432/mydb",
#       "ConnectionPool": {"max_connections": 10, "timeout": 30}
#     },
#     "Logging": {
#       "Level": "INFO",
#       "OutputPath": "/var/log/app.log"
#     },
#     "Features": ["authentication", "api", "admin_panel"]
#   }
# }

# Save to file using the configured path
ApplicationConfig.dump()  # Saves to configs/app_settings.json

# Save to a different file in YAML format
ApplicationConfig.dump(form="yaml", path="configs/app_config.yaml")

# Load configuration
ApplicationConfig.load()  # Loads from configs/app_settings.json

# Access configuration values
db_connection = ApplicationConfig.Database.Connection.value
log_level = ApplicationConfig.Logging.Level.value
features = ApplicationConfig.Features.value

print(f"Database connection: {db_connection}")
print(f"Log level: {log_level}")
print(f"Enabled features: {', '.join(features)}")
```

### Supported Serialization Formats

- JSON (default)
- TOML
- YAML

## License

MIT
