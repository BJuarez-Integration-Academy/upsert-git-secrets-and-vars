import json, os
from base64 import b64encode
from nacl import encoding, public
import requests

rpath = "/home/runner"
repoPublicKey = os.environ['GIT_REPO_PUBLIC_KEY']
repoKeyId = os.environ['GIT_REPO_KEY_ID']
personalAccessToken = os.environ['GIT_PAT']
ORG_NAME = os.environ['GIT_OWNER']
token = "Bearer " + personalAccessToken
repoNames = set()
header = {
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": token
}

def encrypt(public_key: str, secret_value: str) -> str:
  """Encrypt a Unicode string using the public key."""
  public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(public_key)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode("utf-8")

def upsertSecretOrVariable(url: str, encryptedValue: str, keyId:str) -> str:
    body = {
        "encrypted_value": "",
        "key_id": ""
    }
    body["encrypted_value"] = repoSecrets['value']
    body["key_id"] = repoKeyId
    response = requests.request("PUT",url,headers=header,data=json.dumps(body))
    
    if response.status_code == 201:
        print("Secret "+repoSecrets['name']+" created successfully")
    else:
        if response.status_code == 204:
            print("Secret "+repoSecrets['name']+" updated successfully")
        else:
            print("Error: "+response.text)
    return ""

print(rpath)

with open(rpath + "/payload.json") as f:
    payload = json.load(f)



for repoData in payload['repoSecrets']:
    print('*************************************')
    print(repoData['repoName'])
    for repoSecrets in repoData['repoSecret']:
        repoSecrets['value'] = encrypt(repoPublicKey, repoSecrets['value'])
        url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoData['repoName']+"/actions/secrets/"+repoSecrets['name']
        upsertSecretOrVariable(url,repoSecrets['value'],repoKeyId)
        repoNames.add(repoData['repoName'])

for repo in repoNames:
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repo+"/actions/workflows"
    getResp = requests.get(url, headers = header)
    if getResp.status_code == 200:
        print("====> Triggering "+repo +" Workflow")
        getResp = json.loads(getResp.text) 
        wfId=getResp['workflows'][0]['id']
        print(wfId)
        url = "https://api.github.com/repos/"+ORG_NAME+"/"+repo+"/actions/workflows/"+str(wfId)+"/dispatches"
        request = {
            "ref":"dev"
        }
        response = requests.request("POST",url,headers=header,data=json.dumps(request))
        if response.status_code == 204 :
            print("====> Status: Wf Triggered Successfully")

    
        