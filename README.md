# MSFabricStuff
things i've found useful in working with microsoft fabric

* Refresh PowerBI Semantic Model.ipynb - can be used in a Fabric pipeline, passing dataset_id and workspace_id as parameters, to request refresh of a Fabric Semantic Model. You really should use an Azure Key Vault to store any secrets, as shown in [this YouTube video](https://www.youtube.com/watch?v=PKOdWsDvme0), but i wanted to keep the code / setup here small for quick POCs. 
