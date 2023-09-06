import requests
import json

from .pztools import createbody

class ConnectionBPM:
  def __init__(self, baseURL, clientid, clientsecret):
    """
    baseURL: String
    Link to your Bizagi project
    clientid and clientsecret: String
    Authentication details
    """
    self.baseURL = baseURL
    self.auth = (clientid, clientsecret)

    self.endpoints = {
      'getprocesses': '/odata/metadata/processes',
      'token': '/oauth2/server/token',
      'entities': "/odata/data/entities"
    }

    print('\n=> Initiating connection to Bizagi BPM...\n')
    try:
      self._gettoken()  
    except:
      raise ConnectionError('\n\tSomething went wrong with the connection.\n\tCheck the baseURL and BIZAGI server availability') 
    else:
      self.headers = {
          "Authorization": self.BTOKEN
      }
      print('\n=> Successfully connected to Bizagi.')

  def _gettoken(self):
    body = {
        'grant_type':'client_credentials',
        'scope':'api'
    }  
    tokenr = requests.post(self.baseURL+self.endpoints['token'],
                               data=body,
                               auth=self.auth)   
    self.BTOKEN = f"Bearer {tokenr.json()['access_token']}" 
    
  def get_processes(self, lookupid = -1):
      r = requests.get(self.baseURL+self.endpoints['getprocesses'],
                       headers=self.headers)
      pr_names = ''
      for proc in r.json()['value']:
          """
          dict_keys(
              ['@odata.id', 'id', 'name', 'displayName', 
              'entityId', 'parameters', 'template', 
              'processId', 'processType']
          )
          """
          pr_names += proc['name'] + '\n'
      print('\nProcesses structure:')
      print(r.json()['value'][0].keys())
      print('\nLookup:')
      print('Name: ', r.json()['value'][lookupid]['name'])
      print(r.json()['value'][lookupid]['@odata.id'])
      print()
      return pr_names

  def get_oneprocess(self, prid='a88c3aab-a94b-49c5-b83b-5b845d721d86'):    
      end = f'processes({prid})'
      link = self.baseURL+'odata/metadata/' + end
      r = requests.get(link,
                       headers=self.headers)
      print(r.text)


  def get_ents(self):    
      end = self.endpoints['entities']
      link = self.baseURL + end
      r = requests.get(link,
                       headers=self.headers)    
      for ent in r.json()['value']:        
          if ent['name'].lower().find('city') != -1 or ent['name'].lower().find('country') != -1:
              print(ent)    

  def get_country(self):
      end = '/odata/data/entities(eb188de4-f35e-4fc9-bac1-383cf1231c88)/values'
      link = self.baseURL + end
      r = requests.get(link,
                       headers=self.headers)    
      return r.text

  def get_city(self):
    end = "/odata/data/processes(a88c3aab-a94b-49c5-b83b-5b845d721d86)/relatedEntities(2af0f2a4-f72e-4c6b-8a9d-c392d14959db)/values"          
    #end = '/odata/data/entities(73fa9934-705f-4aea-a754-5a15a0aeb121)/values'
    link = self.baseURL + end
    r = requests.get(link,
                      headers=self.headers)    
    return r.text

  def get_relatedents(self, processid = 'a88c3aab-a94b-49c5-b83b-5b845d721d86'):
    end = f'/odata/data/processes({processid})/relatedEntities'
    r = requests.get(self.baseURL+end,
                      headers=self.headers)    
    return r.text

  def post_start(self, processid, body, headers=None):
    if headers is None:
      headers = self.headers
      headers['Content-Type'] = 'application/json'

    end = f'/odata/data/processes({processid})/start'
    print('\n=> starting: ', end)    
    
    r = requests.post(self.baseURL+end,
                      data=json.dumps(body),
                      headers=headers)    
    return r.text


    
class Process:
  def __init__(self, processid: str, connection: ConnectionBPM,
               startstructure:list[str]):
    self.pid = processid
    self.connection = connection
    self.headers = connection.headers
    self.headers['Content-Type'] = 'application/json'

    self.structures = {}
    self.clearbody()

    self.setstartstructure(startstructure)

  def setstructure(self, name:str, structure:list[str]):
    self.structures[name] = structure

  def setstartstructure(self, structure:list[str]):
    self.setstructure('start', structure)

  def setstartbody(self, values:list[str]):
    self.body = createbody("startParameters", self.structures['start'], values)

  def clearbody(self):
    self.body = ""

  def start(self, values:list[str]):
    self.setstartbody(values)
    print(self.connection.post_start(processid=self.pid, body=self.body, headers=self.headers))

    self.clearbody()



# def post_StartTAMS(headers):
#   import json
#   headers['Content-Type'] = 'application/json'
#   end = 'odata/data/processes(939babe9-54ac-47de-b692-1a29b16dbb14)/start'
#   print('\n=> starting: ', end)
#   params = []
#   body = {
#     "startParameters": [
       
#     ]
#   }  
#   r = requests.post(baseURL+end,
#                     data=json.dumps(body),
#                     headers=headers)   
     
#   return r.text  






