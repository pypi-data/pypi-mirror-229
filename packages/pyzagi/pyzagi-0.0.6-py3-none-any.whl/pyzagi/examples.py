"""
Bizagi OUTPUT/RESPONSE EXAMPLES
Results of PYZAGI usage

This is not an executable file
"""

@getprocesses()
# dict_keys of 'getprocesses' response:
(['@odata.context', '@odata.totalCount', 'value'])
# where 'value' is a list of available processes from the provided Bizagi project

# dict_keys of response.json()['value'][i]:
(['@odata.id', 'id', 'name', 
  'displayName', 'entityId', 'parameters',
  'template', 'processId', 'processType']) 

@oneprocess()
# OUTPUT:
{
  "@odata.context": ".../odata/metadata/$metadata#processes(a88c3aab-a94b-49c5-b83b-5b845d721d86)",
  "@odata.id": ".../odata/metadata/processes(a88c3aab-a94b-49c5-b83b-5b845d721d86)",
  "id": "a88c3aab-a94b-49c5-b83b-5b845d721d86",
  "name": "Simplerequest",
  "displayName": "Simple request",
  "entityId": "04ef0912-b730-492e-9724-b0b24c503859",
  "parameters": [
    {
      "id": "25c94f6c-c653-46c4-8983-eb50a3dc39df",
      "name": "Start date",
      "xpath": "Simplerequest.Requestdata.Startdate",
      "type": "DateTime"
    },
    {
      "id": "47b7ded1-ad53-4140-b4b8-2cf7b3c38bf3",
      "name": "End date",
      "xpath": "Simplerequest.Requestdata.Enddate",
      "type": "DateTime"
    },
    {
      "id": "16dc7670-cc3f-4f43-8a99-19d2e9f7c79f",
      "name": "Country",
      "xpath": "Simplerequest.Requestdata.City.Country",
      "type": "Entity"
    },
    {
      "id": "efdf136a-549b-46e1-9fa4-6b18b8c04608",
      "name": "City",
      "xpath": "Simplerequest.Requestdata.City",
      "type": "Entity"
    },
    {
      "id": "bdbde85f-b395-4611-9a3e-f20fae9e025a",
      "name": "Commentary",
      "xpath": "Simplerequest.Requestdata.Commentary",
      "type": "VarChar"
    }
  ],
  "template": [],
  "processId": 37,
  "processType": "Process"
}


@getents()
# OUTPUT (Country)
{'@odata.id': '.../odata/data/entities(eb188de4-f35e-4fc9-bac1-383cf1231c88)',
  'id': 'eb188de4-f35e-4fc9-bac1-383cf1231c88', 
  'name': 'Country', 
  'displayName': 'Country',
  'type': 'Parameter', 
  'template': [{'name': 'Code', 'xpath': 'Code', 'type': 'VarChar'}, 
               {'name': 'Name', 'xpath': 'Name', 'type': 'VarChar'}, 
               {'name': 'Disabled', 'xpath': 'Disabled', 'type': 'Boolean'}]}

@get_country()
# Country values (one value example with full structure)
{
  "@odata.context": "https://dev-bizenv3-presalesea08.bizagi.com/odata/data/$metadata#entities(eb188de4-f35e-4fc9-bac1-383cf1231c88)/values",
  "@odata.totalCount": 3,
  "value": [
    {
      "@odata.id": "https://dev-bizenv3-presalesea08.bizagi.com/odata/data/entities(eb188de4-f35e-4fc9-bac1-383cf1231c88)/values(c8127415-66c3-45a3-b6ce-af99fe146a00)",  
      "id": "c8127415-66c3-45a3-b6ce-af99fe146a00",
      "parameters": [
        {
          "xpath": "Code",
          "value": "Spain"
        },
        {
          "xpath": "Name",
          "value": "Spain"
        },
        {
          "xpath": "dsbl",
          "value": False
        }
  ]}]}


@getrelatedents()
# Output
{
  "@odata.context": "https://dev-bizenv3-presalesea08.bizagi.com/odata/data/$metadata#processes(a88c3aab-a94b-49c5-b83b-5b845d721d86)/relatedEntities",
  "value": [
    {
      "@odata.id": "https://dev-bizenv3-presalesea08.bizagi.com/odata/data/processes(a88c3aab-a94b-49c5-b83b-5b845d721d86)/relatedEntities(2af0f2a4-f72e-4c6b-8a9d-c392d14959db)",  
      "id": "2af0f2a4-f72e-4c6b-8a9d-c392d14959db",
      "name": "City",
      "xpath": "Simplerequest.Requestdata.City"
    }
  ]
}