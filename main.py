import os
import json, urllib
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request
app = Flask(__name__)

BASEURL = "http://fhir2.healthintersections.com.au/open/"
JSON = "text/json&"
SEARCH = "/_search?_format="
SEARCHURL = SEARCH + JSON
SORTURL = "&search-sort=_id"

janegriffinid = 'ad2f3d7c%2D4274%2D4422%2Da10a%2D8e2bc99c40'

@app.route('/patient')
def getPatient(firstname = "Jane", lastname = "Griffin"):
# Request: http://fhir2.healthintersections.com.au/open/Patient/_search?_format=text/json&family=griffin&name=jane&search-sort=_id
	firstname = request.args.get('firstname')
	lastname = request.args.get('lastname')
	if(firstname is None):
		firstname = "Jane"
	if(lastname is None):
		lastname = "Griffin"

	url = BASEURL + "Patient" + SEARCHURL + "family=" + lastname +"&name=" + firstname + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	patient = {}
	patient['First Name'] = firstname
	patient['Last Name'] = lastname
	patient['Birthday'] = data['entry'][0]['resource']['birthDate']
	patient['Gender'] = data['entry'][0]['resource']['gender']

	dateformat = "%Y-%m-%d"
	born = datetime.strptime(patient['Birthday'], dateformat)
	today = datetime.today()
	patient['Age'] = str(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))
	patient['Id'] = data['entry'][0]['resource']['id']
	patient['Picture'] = "http://www.deludeddiva.com/wp-content/uploads/2012/09/mean_thumb.jpg"

	return jsonify(**patient)

@app.route('/allergies')
def getAllergies(id = janegriffinid):
	url = BASEURL + "AllergyIntolerance" + SEARCHURL + "patient._id=" + janegriffinid + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	allergieslist = []
	for aller in data['entry']:
		allergy = {}
		allergy['AllergyId'] = aller['resource']['id']
		allergy['PractitionerId'] = aller['resource']['recorder']['reference']
		allergy['PatientId'] = aller['resource']['patient']['reference']
		allergy['AllergyCode'] = aller['resource']['substance']['coding'][0]['code']
		allergy['AllergyDisplay'] = aller['resource']['substance']['coding'][0]['display']
		allergy['Status'] = aller['resource']['status']
		allergieslist.append(allergy)
	allergies = {"Allergies":allergieslist}

	return jsonify(**allergies)
#search-id=c6fba785-9c00-4505-b42c-499dd43e8b&&patient._id=ad2f3d7c%2D4274%2D4422%2Da10a%2D8e2bc99c40&search-sort=_id 


@app.route('/medications')
def getMedications(id = janegriffinid):
	url = BASEURL + "MedicationOrder" + SEARCHURL + "patient._id=" + janegriffinid + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	medicationlist = []
	for meds in data['entry']:
	    medication = {}
	    medication['OrderId'] = meds['resource']['id'] 
	    medication['PatientId'] = meds['resource']['patient']['reference']
	    medication['PractitionerId'] = meds['resource']['prescriber']['reference']
	    medication['EncounterId'] = meds['resource']['encounter']['reference']
	    medication['ConditionId'] = meds['resource']['reasonReference']['reference']
	    medication['PrescriptionCode'] = meds['resource']['medicationCodeableConcept']['coding'][0]['code']
	    medication['PrescriptionDisplay'] = meds['resource']['medicationCodeableConcept']['coding'][0]['display']
	    medicationlist.append(medication)

	medications = {"Medications":medicationlist}
	return jsonify(**medications)

@app.route('/observations')
def getObservations(id = janegriffinid):
	url = BASEURL + "Observation" + SEARCHURL + "patient._id=" + janegriffinid + SORTURL
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	observationlist = []
	for obs in data['entry']:
		observation = {}
		observation['ObservationId'] = obs['resource']['id']
		try:
		    observation['ObservationCategory'] = obs['resource']['category']['text']
		except KeyError:
		    observation['ObservationCategory'] = 'Medical'

		try:
		    observation['SubjectId'] = obs['subject']['reference']
		except KeyError:
		    observation['SubjectId'] = janegriffinid
		
		try:
		    observation['ObservationDetails'] = obs['resource']['category']['valueCodeableConcept']['coding'][0]['display']
		except KeyError:
		    try:
		        observation['ObservationDetails'] = obs['resource']['code']['text']
		    except KeyError:
		        try:
		        	observation['ObservationDetails'] = obs['resource']['valueString']
		        except KeyError:
		        	try:
		        		observation['ObservationDetails'] = obs['resource']['code']['coding'][0]['display']
		        	except KeyError:
		        		observation['ObservationDetails'] = 'Keep Trying'
		
		try:
			observation['ObservationInterpretation'] = obs['resource']['interpretation']['text']
		except KeyError:
			observation['ObservationInterpretation'] = "N/A"

		value = {}
		valueslist = []
		try:
			for val in obs['resource']['component']:
				value['Measurement'] = val['code']['coding'][0]['display']
				value['Value'] = val['valueQuantity']['value']
				value['Unit'] = val['valueQuantity']['unit']
				valueslist.append(value)
			observation["Measurements"] = valueslist
		except KeyError:
			try:
				value['Measurement'] = obs['resource']['code']['coding'][0]['display']
				value['Value'] = obs['resource']['valueQuantity']['value']
				value['Unit'] = obs['resource']['valueQuantity']['unit']
				valueslist.append(value)
				observation["Measurements"] = valueslist
			except KeyError:
				observation["Measurements"] = "N/A"

		observationlist.append(observation)
	
	observations = {"Observations":observationlist}
	return jsonify(**observations)

@app.route('/encounter')
def getEncounter(enc_id = 65):
	enc_id = request.args.get('enc_id')
	if(enc_id is None):
		enc_id = 65
	url = BASEURL + 'Encounter' + SEARCHURL + "_id=" +str(enc_id)
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	enc = {}
	enc['EncounterId'] = data['entry'][0]['resource']['id']
	enc['PatiendId'] = data['entry'][0]['resource']['patient']['reference']
	enc['PractitionerId'] = data['entry'][0]['resource']['participant'][0]['individual']['reference']
	enc['StartDate'] = data['entry'][0]['resource']['period']['start']
	enc['EndDate'] = data['entry'][0]['resource']['period']['end']
	enc['LocationId'] = data['entry'][0]['resource']['location'][0]['location']['reference']
	enc['ServiceProviderId'] = data['entry'][0]['resource']['serviceProvider']['reference']
	return jsonify(**enc)

@app.route('/conditions')
def getConditions():
	url = BASEURL + 'Condition' + SEARCHURL + "patient=" + janegriffinid
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	conditionlist = []
	for cond in data['entry']:
		condition = {}
		condition['ConditionId'] = cond['resource']['id']
		condition['PatiendId'] = cond['resource']['patient']['reference']
		condition['EncounterId'] = cond['resource']['encounter']['reference']
		condition['PractitionerId'] = cond['resource']['asserter']['reference']
		condition['ConditionDisplay'] = cond['resource']['code']['coding'][0]['display']
		condition['ConditionSeverity'] = cond['resource']['severity']['coding'][0]['display']
		condition['ConditionProblem'] = cond['resource']['category']['coding'][0]['display']		
		conditionlist.append(condition)
	conditions = {"Conditions":conditionlist}
	return jsonify(**conditions)

@app.route('/provider')
def getProvider():
	prov_id = request.args.get('prov_id')
	if(prov_id is None):
		prov_id = "e0961452-816e-4d3d-bfaa-a9bec791bc"
	url = BASEURL + 'Practitioner' + SEARCHURL + "_id=" + prov_id
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	prac = {}
	prac['PractitionerId'] = data['id']
	name = data['entry'][0]['resource']['name']
	prac['FirstName'] = name['given'][0]
	prac['LastName'] = name['family'][0]
	prac['Suffix'] = name['suffix'][0]
	prac['Role'] = data['entry'][0]['resource']['practitionerRole'][0]['role']['coding'][0]['display']
	prac['OrganizationId'] = data['entry'][0]['resource']['practitionerRole'][0]['managingOrganization']['reference']
	return jsonify(**prac)

@app.route('/organization')
def getOrganization():
	org_id = request.args.get('prov_id')
	if(org_id is None):
		org_id = "76feefd6-0d84-436f-b41f-2f9627d358"

	url = BASEURL + 'Organization' + SEARCHURL + "_id=" + org_id
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	org = {}
	org['OrganizationId'] = data['id']
	org['Name'] = data['entry'][0]['resource']['name']
	return jsonify(**org)

@app.route('/referrals')
def getReferrals():
	url = 'http://fhir2.healthintersections.com.au/open/Practitioner?_format=json'
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	doctorlist = []
	for doc in data['entry']:
		doctor = {}
		doctor['PractitionerId'] = data['id']
		name = doc['resource']['name']
		doctor['FirstName'] = name['given'][0]
		doctor['LastName'] = name['family'][0]
		try:
			doctor['Suffix'] = name['suffix'][0]
		except KeyError:
			doctor['Suffix'] = ''

		try: 
			doctor['Role'] = doc['resource']['practitionerRole'][0]['role']['coding'][0]['display']
		except KeyError:
			doctor['Role'] = ''
		
		try:
			doctor['OrganizationId'] = doc['resource']['practitionerRole'][0]['managingOrganization']['reference']
		except KeyError:
			doctor['Organization'] = ''
		doctorlist.append(doctor)
	doctors = {'Practitioners': doctorlist}
	return jsonify(**doctors)


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug = True)
