# Import libraries
import os
import yaml
import click
from jinja2 import Environment, BaseLoader

static_template = """{{- role.existing_readme -}}

# Generated Documentation
## {{ role.name }}
Description: {{ role.meta.galaxy_info.description or 'Not available.' }}

### Defaults
{% if role.defaults -%}
{% for key, value in role.defaults.items() -%}
- **{{ key }}**: `{{ value }}`
{% endfor -%}
{%- else -%}
No defaults available.
{%- endif %}

### Vars
{% if role.vars -%}
{% for key, value in role.vars.items() -%}
- **{{ key }}**: `{{ value }}`
{% endfor -%}
{%- else -%}
No vars available.
{%- endif %}

### Tasks
{%- if role.tasks|length == 1 and role.tasks[0]['file'] == 'main.yml' %}
| Name | Module |
| ---- | ------ |
{%- for task in role.tasks[0]['tasks'] %}
| {{ task.name }} | {{ task.module }} |
{%- endfor %}
{%- else %}
{% for taskfile in role.tasks %}
#### File: {{ taskfile.file }}
| Name | Module |
| ---- | ------ |
{%- for task in taskfile.tasks %}
| {{ task.name }} | {{ task.module }} |
{%- endfor %}
{% endfor %}
{%- endif %}

{% if role.playbook -%}
## Playbook
```yml
{{ role.playbook }}
```
{%- endif %}

{% if role.meta.galaxy_info -%}
## Author Information
{{ role.meta.galaxy_info.author or 'Unknown Author' }}

#### License
{{ role.meta.galaxy_info.license or 'No license specified.' }}

#### Minimum Ansible Version
{{ role.meta.galaxy_info.min_ansible_version or 'No minimum version specified.' }}

#### Platforms
{% if role.meta.galaxy_info.platforms -%}
{% for platform in role.meta.galaxy_info.platforms -%}
- **{{ platform.name }}**: {{ ", ".join(platform.versions) }}
{% endfor -%}
{%- else -%}
No platforms specified.
{%- endif %}
{%- endif %}
"""

# Initialize the Jinja2 Environment
env = Environment(loader=BaseLoader)
env.from_string(static_template)

# Function to load a YAML file
def load_yaml_file(filepath):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        new_lines = []
        skip = False
        for line in lines:
            stripped_line = line.strip()
            if skip:
                if stripped_line == "":
                    skip = False
                continue

            if "!vault |" in stripped_line:
                parts = stripped_line.split(":")
                var_name = parts[0].strip()
                new_lines.append(f"{var_name}: ENCRYPTED_WITH_ANSIBLE_VAULT\n")
                skip = True
            else:
                new_lines.append(line)

        data = yaml.safe_load(''.join(new_lines))
        
        return data
    except (FileNotFoundError, yaml.constructor.ConstructorError) as e:
        print(f"Error loading {filepath}: {e}")
        return None


# Function to process tasks for special keys like 'block'
def process_special_task_keys(task):
    tasks = []
    if 'block' in task:
        for sub_task in task['block']:
            processed_tasks = process_special_task_keys(sub_task)
            tasks.extend(processed_tasks)
    elif 'rescue' in task:
        for sub_task in task['rescue']:
            processed_tasks = process_special_task_keys(sub_task)
            tasks.extend(processed_tasks)
    else:
        task_name = task.get('name', 'Unnamed')
        task_module = list(task.keys())[1] if 'name' in task else list(task.keys())[0]
        tasks.append({
            'name': task_name,
            'module': task_module
        })
    return tasks


@click.command()
@click.option('--role', default='./role', help='Path to the Ansible role directory.')
@click.option('--playbook', default=None, help='Path to the playbook file.')
def doc_the_role(role, playbook):
    role_path = os.path.abspath(role)
    if not os.path.exists(role_path) or not os.path.isdir(role_path):
        print(f"Folder {role_path} does not exist.")
        return

    playbook_content = None
    if playbook:
        try:
            with open(playbook, 'r') as f:
                playbook_content = f.read()
        except FileNotFoundError:
            print('playbook not found:', playbook)
        except Exception as e:
            print('playbook import error:', e)

    document_role(role_path, playbook_content)
    
def document_role(role_path, playbook_content):
    role_name = os.path.basename(role_path)
    readme_path = os.path.join(role_path, "README.md")
    meta_path = os.path.join(role_path, "meta", "main.yml")

    defaults_data = load_yaml_file(os.path.join(role_path, "defaults", "main.yml")) or {}
    vars_data = load_yaml_file(os.path.join(role_path, "vars", "main.yml")) or {}

    role_info = {
        "name": role_name,
        "defaults": defaults_data,
        "vars": vars_data,
        "tasks": [],
        "meta": load_yaml_file(meta_path) or {},
        "playbook": playbook_content
    }

    tasks_dir = os.path.join(role_path, "tasks")
    role_info["tasks"] = []

    if os.path.exists(tasks_dir) and os.path.isdir(tasks_dir):
        for task_file in os.listdir(tasks_dir):
            if task_file.endswith(".yml"):
                tasks_data = load_yaml_file(os.path.join(tasks_dir, task_file))
                if tasks_data:
                    task_info = {'file': task_file, 'tasks': []}
                    for task in tasks_data:
                        if task and len(task.keys()) > 0:
                            processed_tasks = process_special_task_keys(task)
                            task_info['tasks'].extend(processed_tasks)
                    role_info["tasks"].append(task_info)

    if os.path.exists(readme_path):
        os.remove(readme_path)

    role_info["existing_readme"] = ""

    # Render the static template
    template = env.from_string(static_template)
    output = template.render(role=role_info)

    with open(readme_path, "w") as f:
        f.write(output)

    print('Documentation generated at:', readme_path)

if __name__ == '__main__':
    doc_the_role()
