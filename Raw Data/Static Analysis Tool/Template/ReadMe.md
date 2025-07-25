This is a sample folder. Please refer to the structure of this folder when filling in the coding rule information for other analysis tools.

```
├── README.md  
    # Instruction file for the coding rule collection of the target tool.

├── Tool Information  
    # Contains information about the tool.

│   ├── ToolBasicInfo.json  
        # Includes the basic information of the target tool and the aggregated information obtained after collecting the Rule Information. 
        # Note: The contents of this file are for design reference only.)

├── Scripts  
    # Stores analysis scripts for the target tool, covering the entire process from pulling the project from Git → analyzing the repository code → saving rule information.

└──  Rule Information  
    # Stores the coding rule information directly collected by the Scripts.  
    # Note: This folder is intended only for storing raw data, ensure the information is complete and comprehensive, without adding any post-analysis content.
```



**Note:** The current structure is for demonstration purposes. If it is found to be unsuitable in practice, it can be adjusted as needed through discussion.