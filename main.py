import json,os,glob
import localModule as lm

rpath = os.environ['GITHUB_ROOT_DIR']
#rpath = os.path.dirname(__file__) #Used for local testing
repoNames = set() #Using set to store unic values

#Getting the .json file name
files = glob.glob("*.json")

#Getting the environment from the file name
env = files[0].split("_")
env = env[1].split(".")
env = env[0]
print("\n====>Executing on [" + env + "] environment\n")

#Reading decrypted file
with open(rpath + "/"+files[0]) as f:
    payload = json.load(f)

#Upsert git actions org secrets
if len(payload['orgGithubActions']['secretList']) > 0:
    print('****************ORG Secrets*********************')
    for orgSecret in payload['orgGithubActions']['secretList']:
        #lm.upsertOrgSecret(orgSecret['name'], orgSecret['value'])
        print("Secret Name: " + orgSecret['name'])

#Upsert git actions org variables
if len(payload['orgGithubActions']['variableList']) > 0:
    print('***************ORG Variables**********************')
    for orgVariable in payload['orgGithubActions']['variableList']:
        #lm.upsertOrgVariable(orgVariable['name'], orgVariable['value'])
        print("Variable Name: " + orgVariable['name'])

if len(payload['orgGithubActions']['reposToTrigger']) > 0:
    print("[ORG level]-Triggering workflows from below repos:")
    for repo in payload['orgGithubActions']['reposToTrigger']:
        print("Repo Name: " + repo)
        lm.triggerWorkflow(repo, env)
          
#Upsert git actions repo secrets/variables
if len(payload['repoGithubActions']) > 0:
    print('*****************REPO Secrets and Variables********************')
    for repoData in payload['repoGithubActions']:
        print("====>REPO Name: " + repoData['repoName'])
        repoNames.add(repoData['repoName'])
        for secret in repoData['secretList']:
            print("Secret Name: " + secret['name'])
            lm.upsertRepoSecret(repoData['repoName'], secret['name'], secret['value'])
        for variable in repoData['variableList']:
            print("Variable Name: " + variable['name'])
            lm.upsertRepoVariable(repoData['repoName'], variable['name'], variable['value'])
            
        
#Triggering git actions workflows
if len(repoNames) > 0:
    print("[REPO level]-Triggering workflows from below repos:")
    for repo in repoNames:
        print("Repo Name: " + repo)
        lm.triggerWorkflow(repo, env)
        
