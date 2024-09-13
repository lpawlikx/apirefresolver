import yaml
import copy


def resolve_reference(root, ref_path, resolved_refs):
    if ref_path in resolved_refs:
        return resolved_refs[ref_path]

    parts = ref_path.split('/')
    current = root
    for part in parts[1:]:
        if part in current:
            current = current[part]
        else:
            return None

    resolved_refs[ref_path] = {}

    resolved = deep_resolve(copy.deepcopy(current), root, resolved_refs)
    resolved_refs[ref_path] = resolved
    return resolved


def deep_resolve(data, root, resolved_refs):
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if key == '$ref' and isinstance(value, str):
                resolved = resolve_reference(root, value, resolved_refs)
                if resolved is not None:
                    # Replace the entire dict with the resolved object
                    return deep_resolve(resolved, root, resolved_refs)
                else:
                    # If reference not found, keep the original reference
                    new_dict[key] = value
            else:
                new_dict[key] = deep_resolve(value, root, resolved_refs)
        return new_dict
    elif isinstance(data, list):
        return [deep_resolve(item, root, resolved_refs) for item in data]
    else:
        return data


def parse_and_resolve_yaml(file_path):
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    resolved_refs = {}
    resolved_data = deep_resolve(yaml_data, yaml_data, resolved_refs)
    return resolved_data


def save_resolved_yaml(data, output_file):
    with open(output_file, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)


def main():
    input_file = 'open-api-schema.yaml'
    output_file = 'output.yaml'

    resolved_yaml = parse_and_resolve_yaml(input_file)
    save_resolved_yaml(resolved_yaml, output_file)

    print(f"Resolved YAML saved to {output_file}")


if __name__ == "__main__":
    main()
