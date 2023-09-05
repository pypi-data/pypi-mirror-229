from src.constants.modules import MODULES_FOLDER, MODULES_FILES
from src.constants.files import PROJECT_FILES
from jinja2 import Environment, FileSystemLoader


def create_project_files(base_path):
    """
    Creates project files at the specified base path.

    Args:
        base_path (str or Path): The base path where the project files will be created.

    Returns:
        None
    """

    for file in PROJECT_FILES:
        file_path = base_path / file
        with file_path.open("w+", encoding="utf-8"):
            pass


def create_modules(base_path):
    """
    Creates modules in the specified base path.

    Args:
        base_path (str): The base path where the modules will be created.

    Returns:
        None: This function does not return anything.
    """

    modules_path = base_path / "modules"
    modules_path.mkdir(exist_ok=True)

    for folder in MODULES_FOLDER:
        folder_path = modules_path / folder
        folder_path.mkdir(exist_ok=True)

        with folder_path:
            for file in MODULES_FILES:
                file_path = folder_path / file
                with file_path.open("w+", encoding="utf-8"):
                    pass


def create_env_folders(base_path):
    """
    Create environment folders within the given base path.

    Args:
        base_path (str): The base path where the environment folders will be created.

    Returns:
        None
    """

    envs_path = base_path / "environments"
    envs_path.mkdir(exist_ok=True)
    envs = ["production", "staging", "development"]
    for e in envs:
        env_path = envs_path / e
        env_path.mkdir(exist_ok=True)

        tfvars_file_path = env_path / f"{e}.tfvars"
        with tfvars_file_path.open("w", encoding="utf-8"):
            pass


def create_provider(base_path, cloud):
    """
    Creates a provider configuration file for the specified cloud provider.

    Args:
        base_path (Path): The base path where the provider configuration file should be created.
        cloud (str): The name of the cloud provider.

    Returns:
        None
    """

    template_cloud = Environment(loader=FileSystemLoader("templates"))
    file_path = base_path / "provider.tf"

    template = template_cloud.get_template(f"provider_{cloud}.j2")
    rendered_content = template.render()

    with file_path.open("w", encoding="utf-8") as f:
        f.write(rendered_content)


def create_gitignore(base_path):
    """
    Generates a .gitignore file in the specified base directory.

    Args:
        base_path (Path): The base directory where the .gitignore file will be created.

    Returns:
        None
    """
    template_gitignore = Environment(loader=FileSystemLoader("templates"))
    file_path = base_path / ".gitignore"

    template = template_gitignore.get_template("gitignore.j2")
    rendered_content = template.render()

    with file_path.open("w", encoding="utf-8") as f:
        f.write(rendered_content)
