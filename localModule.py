import json, os,requests
from base64 import b64encode
from nacl import encoding, public


personalAccessToken = os.environ['POC_GIT_PAT']
ORG_NAME = os.environ['POC_GIT_OWNER']

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

orgVarBody = {
        "name": "",
        "value": "",
        "visibility": "all"
    }

repoVarBody = {
        "name":"workers",
        "value":"2"
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


###############################-Get ORG Public Key Funtion-####################################
def getOrgPublicKey()->dict:
    url= "https://api.github.com/orgs/"+ORG_NAME+"/actions/secrets/public-key"
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

#################################-Upsert ORG Secrets Function-#################################
def upsertOrgSecret(orgSecretName:str, orgSecretValue:str):
    encryptionResources = getOrgPublicKey()
    secretValue = encrypt(encryptionResources["public_key"],orgSecretValue)
    body = {
        "encrypted_value": "",
        "key_id": "",
        "visibility": "all"
    }
    body["encrypted_value"] = secretValue
    body["key_id"] = encryptionResources["key_id"]
    url = "https://api.github.com/orgs/"+ORG_NAME+"/actions/secrets/"+orgSecretName
    response = requests.request("PUT",url,headers=header,data=json.dumps(body))
    
    if response.status_code == 201:
        print("Secret "+orgSecretName+" created successfully")
    else:
        if response.status_code == 204:
            print("Secret "+orgSecretName+" updated successfully")
        else:
            print("Error: "+response.text)

#################################-Create ORG Variables Function-#################################
def createOrgVariable(varName:str, varValue:str)->int:
    url = "https://api.github.com/orgs/"+ORG_NAME+"/actions/variables"
    responseCode = 0
    orgVarBody['name'] = varName
    orgVarBody['value'] = varValue
    response = requests.request("POST",url,headers=header,data=json.dumps(orgVarBody))
    responseCode = response.status_code
    if response.status_code == 201:
        print("Variable "+varName+" created successfully")
    else:
        print("Error: "+response.text)
    return responseCode

#################################-Update ORG Variables Function-#################################
def updateOrgVariable(varName:str, varValue:str)->int:
    url = "https://api.github.com/orgs/"+ORG_NAME+"/actions/variables/"+varName
    responseCode = 0
    orgVarBody['name'] = varName
    orgVarBody['value'] = varValue
    response = requests.request("PATCH",url,headers=header,data=json.dumps(orgVarBody))
    responseCode = response.status_code
    if response.status_code == 204:
        print("Variable "+varName+" updated successfully")
    else:
        print("Error: "+response.text)
    return responseCode

#################################-Upsert ORG Variables Function-#################################
def upsertOrgVariable(varName:str, varValue:str)->int:
    response = createOrgVariable(varName, varValue)
    if response != 201:
        updateOrgVariable(varName, varValue)

#################################-Upsert REPO Secrets Function-#################################
def upsertRepoSecret(repoName: str, secretName:str, secretValue: str):
    
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

#################################-Create REPO Variables Function-#################################
def createRepoVariable(repoName:str, varName:str, varValue:str)-> int:
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/variables"
    repoVarBody['name'] = varName
    repoVarBody['value'] = varValue
    response = requests.request("POST",url,headers=header,data=json.dumps(repoVarBody))
    responseCode = response.status_code
    if response.status_code == 201:
        print("Variable "+varName+" created successfully")
    else:
        print("Error: "+response.text)
    return responseCode

#################################-Update REPO Variables Function-#################################
def updateRepoVariable(repoName:str, varName:str, varValue:str)-> int:
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/variables/"+varName
    repoVarBody['name'] = varName
    repoVarBody['value'] = varValue
    response = requests.request("PATCH",url,headers=header,data=json.dumps(repoVarBody))
    responseCode = response.status_code
    if response.status_code == 204:
        print("Variable "+varName+" updated successfully")
    else:
        print("Error: "+response.text)
    return responseCode

#################################-Upsert REPO Variables Function-#################################
def upsertRepoVariable(repoName:str, varName:str, varValue:str):
    response = createRepoVariable(repoName, varName, varValue)
    if response != 201:
        updateRepoVariable(repoName, varName, varValue)
        
#################################-Trigger Workflow Function-#################################
def triggerWorkflow(repoName: str,env:str):
    url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/workflows"
    getResp = requests.get(url, headers = header)
    if getResp.status_code == 200:
        print("====> Triggering "+repoName +" Workflow")
        getResp = json.loads(getResp.text) 
        wfId=getResp['workflows'][0]['id']
        url = "https://api.github.com/repos/"+ORG_NAME+"/"+repoName+"/actions/workflows/"+str(wfId)+"/dispatches"
        request = {
            "ref": env
        }
        response = requests.request("POST",url,headers=header,data=json.dumps(request))
        if response.status_code == 204 :
            print("====> Status: Wf Triggered Successfully")
        else: print("Error while triggering the workflow from repo: "+ repoName)
    else: print("Error while getting workflow ID from repo: "+ repoName)