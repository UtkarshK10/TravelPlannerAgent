import os
import json


def expand_env_values(value):
    if isinstance(value, dict):
        return {key: expand_env_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [expand_env_values(item) for item in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def remove_unset_env_values(config):
    for server_config in config.values():
        env = server_config.get("env")
        if not isinstance(env, dict):
            continue
        server_config["env"] = {
            key: value
            for key, value in env.items()
            if not (isinstance(value, str) and value.startswith("${") and value.endswith("}"))
        }
    return config


# -------------------------
# MCP Config Loader
# -------------------------
def load_mcp_config(*server_names):
    config_path = os.path.join(os.path.dirname(__file__), 'mcp_config.json')

    with open(config_path, 'r') as f:
        all_configs = remove_unset_env_values(expand_env_values(json.load(f)))

    if len(server_names)==0:
        return all_configs
    
    selected_configs = {}
    for name in server_names:
        if name in all_configs:
            selected_configs[name] = all_configs[name]

    return selected_configs


if __name__ == "__main__":
    print(load_mcp_config('google-calendar'))
