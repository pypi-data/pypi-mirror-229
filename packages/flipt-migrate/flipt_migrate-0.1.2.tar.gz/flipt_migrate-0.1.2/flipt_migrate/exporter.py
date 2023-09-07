import os

from flipt_migrate.models.flipt import Collection
from pydantic_yaml import to_yaml_str


def export_to_yaml(data: Collection, output_path):
    files = []
    for namespace, d in data.namespaces.items():
        f = os.path.join(output_path, f"{namespace}.features.yml")
        files.append(f)
        with open(f, "w") as file:
            file.write(to_yaml_str(d))
    return files
