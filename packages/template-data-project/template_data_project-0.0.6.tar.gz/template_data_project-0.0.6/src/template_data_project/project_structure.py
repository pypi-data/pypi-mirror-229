# Libraraires
import os
import json

# Functions
def create_file(root_dir,file):
    file_path = os.path.join(root_dir, file)
    with open(file_path, "w") as file:
        pass
def create_folder(root_dir,folder):
    if folder =="root":
        return root_dir
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    folder_path = os.path.join(root_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
def create_folder_or_file(root_dir,key,mydict):
    if mydict[key] =="":
        root_dir = create_folder(root_dir,key)
    elif isinstance(mydict[key],list):
        root_dir = create_folder(root_dir,key)
        try:
            for file in mydict[key]:
                create_file(root_dir,file)
        except:
            pass
    elif isinstance(mydict[key],dict):
        root_dir = create_folder(root_dir,key)
        try:
            for item in mydict[key]:
                create_folder_or_file(root_dir,item,mydict[key])
        except:
            pass
    else:
        pass
# content
content = {
    "Documentation":"",
    "Source Code":{"ETL Scripts":["extract.py","transform.py","load.py"],
                    "Data Processing":{"Extract":"","Transform":"","Load":""},
                    "Infrastructure as Code (IaC)":[]  
                    },
    "Data":{"Data raw":"","Data processed":"","Data final":""},
    "Configurations":{"Database Connection Settings":"",
                      "API Keys and Authentication Tokens":"",
                      "Data Processing Rules":"",
                      "Logging and Monitoring Configuration":"",
                      "Environment-Specific Configurations":"",
                      "Data Retention Policies":""},
    "Testing":"",
    "Logs":["Mlog.log"],
    "Reports and Visualizations":{"Notebooks":"",
                                  "BI dashboards":""},
    "Libraries and Dependencies":{"Python Libraries":"",
                                  "Database Drivers":"",
                                  "Big Data and Distributed Computing Frameworks":"",
                                  "Cloud Service SDKs":"",
                                  "Custom Libraries":""},
    "Infrastructure":"",
    "Environments":{"Development":"",
                    "Staging":"",
                    "Production":""},
    "Utilities":"",
    "Archives":"",
    "Tests and Test Data":"",
    "Docker":"",
    "CI/CD":"",
    "root":["setup.py","README.md","LICENSE"]
}
# create project structure
def template(root_dir):
    for key in content:
        create_folder_or_file(root_dir,key,content)
        
if "__main__" =="__name__":
    root_dir = "template_data_project" 
    template(root_dir)
    