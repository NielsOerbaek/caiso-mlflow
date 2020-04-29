import mlflow.azureml

from azureml.core import Workspace
from azureml.core.webservice import AciWebservice, Webservice


# Create or load an existing Azure ML workspace. You can also load an existing workspace using
# Workspace.get(name="<workspace_name>")
workspace_name = "Assignment4"
subscription_id = "a35f11df-45f8-4c96-8b5b-87be3cfca130"
resource_group = "ITU-LSDA2020"
location = "northeurope"
azure_workspace = Workspace.create(name=workspace_name,
                                   subscription_id=subscription_id,
                                   resource_group=resource_group,
                                   location=location,
                                   create_resource_group=True,
                                   exist_ok=True)

# Build an Azure ML container image for deployment
azure_image, azure_model = mlflow.azureml.build_image(model_uri="runs:/a57a7c665dc04d85ab11ee2a2e562a91/model",
                                                      workspace=azure_workspace,
                                                      description="Orkney-Caiso-2",
                                                      synchronous=False)
# If your image build failed, you can access build logs at the following URI:
print("Access the following URI for build logs: {}".format(azure_image.image_build_log_uri))

# Deploy the container image to ACI
webservice_deployment_config = AciWebservice.deploy_configuration()
webservice = Webservice.deploy_from_image(
                    image=azure_image, workspace=azure_workspace, name="orkney-caiso-123")
webservice.wait_for_deployment()

# After the image deployment completes, requests can be posted via HTTP to the new ACI
# webservice's scoring URI. The following example posts a sample input from the wine dataset
# used in the MLflow ElasticNet example:
# https://github.com/mlflow/mlflow/tree/master/examples/sklearn_elasticnet_wine
print("Scoring URI is: %s", webservice.scoring_uri)