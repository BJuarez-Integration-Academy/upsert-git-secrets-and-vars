import json, os,requests
from base64 import b64encode
from nacl import encoding, public


personalAccessToken = os.environ['GIT_PAT']
ORG_NAME = os.environ['GIT_OWNER']

################################-Initializing global vars-##############################################
token = "Bearer " + personalAccessToken
header = {
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": token
}
body = {
        "encrypted_value": "",
        "key_id": ""
    }

#################################-Encrypt Secret Value Function-#################################
def encrypt(repoPublicKey:str, secret_value: str) -> str:
  """Encrypt a Unicode string using the public key."""
  repoPublicKey = public.PublicKey(repoPublicKey.encode("utf-8"), encoding.Base64Encoder())
  sealed_box = public.SealedBox(repoPublicKey)
  encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
  return b64encode(encrypted).decode("utf-8")

###############################-Get Repo Public Key Funtion-####################################
def getRepoPublicKey(repoName:str)->dict:
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/secrets/public-key"
    response = requests.get(url, headers = header)
    encryptionResorces = {
        "Key_id": "",
        "public_key": ""
    }
    if response.status_code == 200:
        response =json.loads(response.text)
        encryptionResorces["key_id"] = response["key_id"]
        encryptionResorces["public_key"] = response["key"]
        print("KeyId and PublicKey generated successfully")
    else:
        print("Error: While generating KeyId and publicKey")
        print("Error: "+response.text)
    return encryptionResorces
        

#################################-Upsert ORG/REPO Secrets Function-#################################
def upsertSecretOrVariable(repoName: str, secretValue: str, secretName:str):
    
    encryptionResources = getRepoPublicKey(repoName)
    secretValue = encrypt(encryptionResources["public_key"],secretValue)
    body["encrypted_value"] = secretValue
    body["key_id"] = encryptionResources["key_id"]
    
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/secrets/"+secretName
    response = requests.request("PUT",url,headers=header,data=json.dumps(body))
    
    if response.status_code == 201:
        print("Secret "+secretName+" created successfully")
    else:
        if response.status_code == 204:
            print("Secret "+secretName+" updated successfully")
        else:
            print("Error: "+response.text)

#################################-Trigger Workflow Function-#################################
def triggerWorkflow(repoName: str):
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/workflows"
    getResp = requests.get(url, headers = header)
    if getResp.status_code == 200:
        print("====> Triggering "+repoName +" Workflow")
        getResp = json.loads(getResp.text) 
        wfId=getResp['workflows'][0]['id']
        url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/workflows/"+str(wfId)+"/dispatches"
        request = {
            "ref":"dev"
        }
        response = requests.request("POST",url,headers=header,data=json.dumps(request))
        if response.status_code == 204 :
            print("====> Status: Wf Triggered Successfully")