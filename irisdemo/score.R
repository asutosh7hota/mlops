# Copyright(c) Microsoft Corporation.
# Licensed under the MIT license.

library(jsonlite)

init <- function()
{
  model_path <- Sys.getenv("AZUREML_MODEL_DIR")
  model <- readRDS(file.path(model_path, "model_trained.rds"))
  message("model is loaded")
  
  function(data)
  {
    input_data <- as.data.frame(fromJSON(data))
    prediction <- predict(model, input_data)
    result <- as.character(prediction)
    toJSON(result)
  }
}