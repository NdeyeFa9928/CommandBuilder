::: mermaid
classDiagram
    class Pipeline {
        +String name
        +String description
        +List~Task~ tasks
    }
    
    class Task {
        +String name
        +String description
        +List~Command~ commands
    }
    
    class Command {
        +String name
        +String description
        +String command
        +List~Argument~ arguments
    }
    
    class Argument {
        +String code
        +String name
        +String description
    }
    
    class YAMLLoader {
        +load_yaml_with_includes(file_path)
        +load_pipeline(pipeline_name, data_root)
    }
    
    class YAMLPipelineLoader {
        +get_yaml_pipelines_directory()
        +list_yaml_pipeline_files()
        +load_yaml_pipeline(file_path)
        +load_yaml_pipelines()
        -resolve_command_includes(command_data)
        -resolve_task_includes(task_data)
    }
    
    Pipeline "1" *-- "many" Task : contains
    Task "1" *-- "many" Command : contains
    Command "1" *-- "many" Argument : contains
    
    YAMLLoader <|-- YAMLPipelineLoader : extends
    YAMLPipelineLoader --> Pipeline : creates
    YAMLPipelineLoader --> Task : creates
    YAMLPipelineLoader --> Command : creates
:::
