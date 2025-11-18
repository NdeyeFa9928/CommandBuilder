"""Tests supplémentaires pour les fonctions internes de `yaml_task_loader` afin d'améliorer la couverture."""

from command_builder.services.yaml_task_loader import (
    merge_task_metadata,
    resolve_command_includes,
)


def test_resolve_command_includes_with_full_definition():
    cmd_data = {"name": "cmd", "command": "echo x"}
    result = resolve_command_includes(cmd_data)
    assert result == [cmd_data]


def test_resolve_command_includes_with_list():
    cmd_list = [
        {"name": "c1"},
        {"name": "c2"},
    ]
    assert resolve_command_includes(cmd_list) == cmd_list


def test_merge_task_metadata_flattens_includes():
    task = {
        "name": "Task",
        "commands": [
            {"name": "cmd1"},
            [
                {"name": "cmd2"},
                {"name": "cmd3"},
            ],
        ],
    }

    merged = merge_task_metadata(task)
    assert len(merged["commands"]) == 3
    names = [c["name"] for c in merged["commands"]]
    assert names == ["cmd1", "cmd2", "cmd3"]
