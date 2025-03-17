# MSFabricStuff
things i've found useful in working with microsoft fabric

## what's here
* azure_keyvault.py: this is just a simple script allowing one to 
  * bulk import secrets to an azure keyvault 
  * generate a handly list of the secret keys for future copy/pasting into code
* refresh_fabric_semantic_model.py: allows one to refresh models in power bi service from python (if you're doing this in a fabric notebook, instead look to MS's [semantic-link](https://pypi.org/project/semantic-link/) package)
* m
  * Convert15to18.m: Power Query function to convert Salesforce case sensitive ids to case insensitive ids
* notebooks
  * load_msgraph_to_lakehouse.ipynb - shows pulling Entra users, groups, group memberships and storing to lakehouse tables
  * delete_all_lakehouse_tables.ipynb - does exactly what it says it does. saves one from clicking endlessly.
* sql
  * get_highest_medallion_tables.sql - when you have silver and bronze and gold tables in the same db / schemas, this just grabs the highest level table and hides the rest

## Links to other places
* [Fabric Toolbox](https://github.com/microsoft/fabric-toolbox) 
* [PBI Monitor](https://github.com/RuiRomano/pbimonitor) get logs to storage for increased retention
* [Fabric CI/CD](https://github.com/microsoft/fabric-cicd)
* [Sempy labs](https://github.com/microsoft/semantic-link-labs)