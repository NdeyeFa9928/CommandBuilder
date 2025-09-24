from pathlib import Path
from command_builder.services.pipeline_loader import load_pipeline

if __name__ == "__main__":
    pipelines_dir = Path(__file__).parent / "command_builder" / "data" / "pipelines"
    pipeline_files = list(pipelines_dir.glob("*.json"))
    
    if not pipeline_files:
        print(f"Aucun fichier pipeline trouvé dans {pipelines_dir}")
    else:
        print(f"{len(pipeline_files)} pipeline(s) trouvé(s) :")
        for i, file in enumerate(pipeline_files, start=1):
            print(f"{i}. {file.name}")

    