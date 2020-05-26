import yaml
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    print("python-dotenv not installed. Not loading .env")
    pass

from azureml.core import (
    Datastore,
    RunConfiguration,
    Experiment,
    Workspace,
    ComputeTarget,
)
from azureml.data.data_reference import DataReference
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.pipeline.core import Pipeline
from azureml.pipeline.steps import PythonScriptStep


with open("conf.yaml", "r") as f:
    conf = yaml.load(f, Loader=yaml.FullLoader)
    auth_config = conf["auth"]
    compute = conf["compute"]

# Authenticate with AzureML
auth = ServicePrincipalAuthentication(
    tenant_id=auth_config["tenant_id"],
    service_principal_id=auth_config["service_principal_id"],
    service_principal_password=os.environ["SP_SECRET"],
)

ws = Workspace(
    subscription_id=auth_config["subscription_id"],
    resource_group=auth_config["resource_group"],
    workspace_name=auth_config["workspace_name"],
    auth=auth,
)


# Usually, the  cluster already exists, so we just fetch
compute_target = next(
    (m for m in ComputeTarget.list(ws) if m.name == compute["name"]), None
)

run_config = RunConfiguration()
run_config.environment.docker.enabled = True
run_config.environment.python.conda_dependencies = CondaDependencies.create(
    conda_packages=[
        "tensorflow=2.0.0",
        "pandas",
        "numpy",
        "matplotlib"
        ],
    pip_packages=[
        "azureml-mlflow==1.5.0"
    ]
)

# Pipeline definition
inputdata = DataReference(
    datastore=Datastore.get(ws, "trainingdata"),
    data_reference_name="data"
)

train_model = PythonScriptStep(
    script_name="./train.py",
    name="fit-nlp-model",
    inputs=[inputdata.as_download(path_on_compute="./data")],
    runconfig=run_config,
    compute_target=compute_target,
)

pipeline = Pipeline(
    workspace=ws,
    steps=[train_model],
    description="Builds Keras model for detecting component defects",
)

if __name__ == "__main__":
    Experiment(ws, "fit-component-defects-model").submit(pipeline).wait_for_completion(
        show_output=True
    )
