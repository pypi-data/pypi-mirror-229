import wandb


def push(project: str, dataset: str, data_dir_path: str, alias: str = "latest"):
    api = wandb.Api()
    artifact = api.artifact(f"{project}/{dataset}:{alias}")
    artifact.add_dir(data_dir_path)
    artifact.save()


def pull(project: str, dataset: str, alias: str = "latest", data_dir_path: str = None):
    api = wandb.Api()
    artifact = api.artifact(f"{project}/{dataset}:{alias}")
    artifact_dir = artifact.download(data_dir_path)
    return artifact_dir
