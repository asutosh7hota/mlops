# Copyright(c) Microsoft Corporation.
# Licensed under the MIT license.

library(azuremlsdk)
library(jsonlite)

ws <- load_workspace_from_config()

# Register the model
#model <- register_model(ws, model_path = "model.rds", model_name = "model.rds")

model <- get_model(ws,
                   id="iris_model_trained"
                  )

# Create environment
r_env <- r_environment(name = "r_env")

# Create inference config
inference_config <- inference_config(
  entry_script = "score.R",
  source_directory = ".",
  environment = r_env)

# Create ACI deployment config
deployment_config <- aci_webservice_deployment_config(cpu_cores = 1,
                                                      memory_gb = 1)

# Deploy the web service
service_name <- paste0('aciservice-', sample(1:100, 1, replace=TRUE))
service <- deploy_model(ws, 
                        service_name, 
                        list(model), 
                        inference_config, 
                        deployment_config)
wait_for_deployment(service, show_output = TRUE)

# If you encounter any issue in deploying the webservice, please visit
# https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-troubleshoot-deployment

# Inferencing
# versicolor
test_data <- data.frame(Sepal.Length = 6.4,
                    Sepal.Width = 2.8,
                    Petal.Length = 4.6,
                    Petal.Width = 1.8)

# Test the web service
predicted_val <- invoke_webservice(service, toJSON(test_data))
predicted_val

# Delete the web service
#delete_webservice(service)
