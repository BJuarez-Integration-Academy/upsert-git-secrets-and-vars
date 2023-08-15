import json
import localModule as lm

rpath = "/home/runner"
#rpath = os.path.dirname(__file__) #Used for local testing
repoNames = set()

#Reading decrypted file
with open(rpath + "/payload.json") as f:
    payload = json.load(f)


#Upsert git actions repo secrets
for repoData in payload['repoSecrets']:
    print('*************************************')
    print(repoData['repoName'])
    for repoSecrets in repoData['repoSecret']:
        lm.upsertSecretOrVariable(repoData['repoName'],repoSecrets['value'],repoSecrets['name'])
        repoNames.add(repoData['repoName'])

#Triggering git actions workflows
for repo in repoNames:
    lm.triggerWorkflow(repo)

    
        