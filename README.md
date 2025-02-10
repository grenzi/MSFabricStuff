# MSFabricStuff
things i've found useful in working with microsoft fabric

* azure_keyvault.py: this is just a simple script allowing one to 
  * bulk import secrets to an azure keyvault 
  * generate a handly list of the secret keys for future copy/pasting into code
* refresh_fabric_semantic_model.py: allows one to refresh models in power bi service from python (if you're doing this in a fabric notebook, instead look to MS's [semantic-link](https://pypi.org/project/semantic-link/) package)