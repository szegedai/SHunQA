# Pipeline Steps

In the start the data will be `{"query": ""}`. Through the pipeline steps it will grow with the different outputs from each step.

## OutOfDomainDetection

This steps add the `ood_class` key to the dictionary. The value will be the prediction from the OOD model.
