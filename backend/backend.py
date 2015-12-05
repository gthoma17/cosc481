import web, ConfigParser, json, string, random, socket, urllib, datetime, boto, base64
from os import path
from identitytoolkit import gitkitclient

#prepare to read config
config = ConfigParser.ConfigParser()
root = path.dirname(path.realpath(__file__))

#determine if we're on a production machine, or testing machine
# load the correct config based on that.  
localIp = socket.gethostbyname(socket.gethostname())
publicIp = urllib.urlopen('https://wtfismyip.com/text').read().rstrip()
if localIp == publicIp: 
	#we're on the internet
	config.read(path.join(root, "backend.cfg"))
else:
	#we're on a local machine
	config.read(path.join(root, "local.cfg"))

urls = (
	"/", "index",
	"/user/(.*)", "user",
	"/user", "newUser",
	"/users/type/(.*)", "userType",
	"/job", "newJob",
	"/job/(.*)", "job",
	"/budgetItem", "budgetItem",
	"/note", "note",
	"/actionItem", "actionItem",
	"/delete/budgetItem", "deleteBudgetItem",
	"/delete/user", "deleteUser",
	"/photo", "photo",
	"/userActionItems", "userActionItems",
	"/userJobs","userJobs"
	)

app = web.application(urls, globals())
db = web.database(dbn='mysql', host=config.get("Database", "host"), port=int(config.get("Database", "port")), user=config.get("Database", "user"), pw=config.get("Database", "password"), db=config.get("Database", "name"), charset='utf8mb4')
s3Bucket = boto.connect_s3(aws_access_key_id=config.get("aws", "access_key_id"), aws_secret_access_key=config.get("aws", "secret_access_key")).get_bucket(config.get("aws", "bucket_name"))
bucketHlq = config.get("aws", "bucket_hlq")

def set_headers():
    web.header('Access-Control-Allow-Origin',      '*')

app.add_processor(web.loadhook(set_headers))

class userJobs:
	def GET(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		jobs = list(db.where('jobs', manager_id=reqUser['id']))
		jobs.extend(list(db.where('jobs', supervisor_id=reqUser['id'])))
		return json.dumps(makeDumpable(jobs))
		
class userActionItems:
	def GET(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		actionItems = list(db.where('actionItems', assigned_user=reqUser['id']))
		return json.dumps(makeDumpable(actionItems))


		
class userType:
	def GET(self, reqTypes):
		#try:
		#	reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		#except IndexError:
		#	return "403 Forbidden"
		outList = []
		if reqTypes == "all":
			outList.extend(list(db.select('jobAppUsers')))
		else:
			types = reqTypes.split("|")
			for reqType in types:
				outList.extend(list(db.select('jobAppUsers', what="id, name, permissionLevel, email, phone",  where="permissionLevel like '%"+reqType+"%'")))
		return json.dumps(outList)
	def POST(self):
		return "Shhhh... the database is sleeping."

class photoFolder:
	def GET(self):
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		#use selected job, and current timestamp to ensure uniquness
		# it shouldn't be possible to add two photos to the same job
		# in one millisecond
		# ... I hope. 
		
		if 'parent_id' not in passedData.keys():
			passedData['parent_id'] = -1

		photoFolder = db.insert('photoFolders', 
					job_id=passedData['job_id'],
					parent_id=passedData['parent_id'],
					name=passedData['name']
				)
		return json.dumps(photoFolder)


class photo:
	def GET(self):
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		#use selected job, and current timestamp to ensure uniquness
		# it shouldn't be possible to add two photos to the same job
		# in one millisecond
		# ... I hope. 
		newFileName = "/images/" 
		newFileName += passedData['job_id'] + "_"
		newFileName += datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3]
		newFileName += passedData['file_extension']

		#add the image to s3

		# get rid of the header that javascript uses.
		img =  passedData['base64_image'].split(';base64,')[1]
		newKey = s3Bucket.new_key(newFileName)
		newKey.content_type = passedData['type'] # content type must be assigned before data
		newKey.set_contents_from_string(base64.b64decode(img))
		newKey.set_acl('public-read')

		#add a link to the image to the database
		#photo folders will be implemented at a later time
		newFileLink = bucketHlq + newFileName

		photo = db.insert('photos', 
					job_id=passedData['job_id'],
					link=newFileLink
				)
		return json.dumps(photo)

class deleteBudgetItem:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if reqUser['permissionLevel'].upper() == "ADMIN" or reqUser['permissionLevel'].upper() == "MANAGER":
			#user can do this
			try:
				theItem = db.where('budgetItems', id=passedData['id'])[0]
			except:
				return "404 Not Found"
			db.delete('budgetItems', where="id="+passedData['id'])
			return "200 OK"
		else:
			return "403 Forbidden"
class deleteUser:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if 	(reqUser['permissionLevel'].upper() == "ADMIN" or reqUser['permissionLevel'].upper() == "MANAGER") and \
			(reqUser['id'] != passedData['id']) :
			#user can do this
			try:
				theItem = db.where('jobAppUsers', id=passedData['id'])[0]
			except:
				return "404 Not Found"
			db.delete('jobAppUsers', where="id="+passedData['id'])
			return "200 OK"
		else:
			return "403 Forbidden"
class actionItem:
	def GET(self):
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if "assigned_user" in passedData:
			db.update("actionItems", where="id = "+str(passedData['id']), 
					assigned_user=passedData['assigned_user']
				)
			return json.dumps(db.where('jobAppUsers', id=passedData['assigned_user'])[0])
		if "complete" in passedData:
			db.update("actionItems", where="id = "+str(passedData['id']), 
						completion_user=reqUser['id'],
						completion_time=datetime.datetime.now().isoformat()
					)
			return json.dumps(makeDumpable(db.where('actionItems', id=passedData['id'])[0]))

		return "481 WTF?"

class note:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		#create a new note
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if not db.where('jobs', id=passedData['job_id']):
			return "403 Forbidden"
		tbl = passedData['tbl']

		if 'id' in passedData: #user passed an ID, they want to update
			db.update(tbl, where="id = "+str(passedData['id']), 
					edit_user=reqUser['id'],
					edit_time=datetime.datetime.now().isoformat()
				)
			if "contents" in passedData:
				db.update(tbl, where="id = "+str(passedData['id']), 
						contents=passedData['contents']
					)
			if "assigned_user" in passedData:
				db.update(tbl, where="id = "+str(passedData['id']), 
						assigned_user=passedData['assigned_user']
					)
			if "completion_user" in passedData:
				db.update(tbl, where="id = "+str(passedData['id']), 
						completion_user=reqUser['id'],
						completion_time=datetime.datetime.now().isoformat()
					)
			if "arrival_time" in passedData:
				date = datetime.datetime.now().strftime("%d/%m/%Y")
				arrivalTime = datetime.datetime.strptime(passedData['arrival_time']+" "+date, "%H:%M %d/%m/%Y")
				db.update(tbl, where="id = "+str(passedData['id']), 
						arrival_time=arrivalTime.isoformat()
					)
			if "departure_time" in passedData:
				date = datetime.datetime.now().strftime("%d/%m/%Y")
				departureTime = datetime.datetime.strptime(passedData['departure_time']+" "+date, "%H:%M %d/%m/%Y")
				db.update(tbl, where="id = "+str(passedData['id']), 
						departure_time=departureTime.isoformat()
					)
			if "people_on_site" in passedData:
				db.update(tbl, where="id = "+str(passedData['id']), 
						people_on_site=passedData['people_on_site']
					)
			return "202 Note Updated"
		else: #no ID passed, user wants to create
			note = db.insert(tbl, 
						job_id=passedData['job_id'],
						author_id=reqUser['id'],
						contents=passedData['contents']
					)
			if tbl == "dailyReports":
				date = datetime.datetime.now().strftime("%d/%m/%Y")
				arrivalTime = datetime.datetime.strptime(passedData['arrival_time']+" "+date, "%H:%M %d/%m/%Y")
				departureTime = datetime.datetime.strptime(passedData['departure_time']+" "+date, "%H:%M %d/%m/%Y")
				db.update(tbl, where="id = "+str(note), 
						arrival_time=arrivalTime.isoformat(),
						departure_time=departureTime.isoformat(),
						people_on_site=passedData['people_on_site']
					)
			if tbl == "actionItems" and "assigned_user" in passedData:
				try:
					assignedUser = db.where('jobAppUsers', name=passedData['assigned_user'])[0]
					db.update(tbl, where="id = "+str(note), 
						assigned_user=passedData['assigned_user']
					)
				except:
					pass
			return json.dumps(note)

class index:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self): 
		return "Shhhh... the database is sleeping."
class newJob:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if db.where('jobs', name=passedData['name']):
			return "403 Forbidden"
		#are there any people that shouldn't be allowed to create jobs?
		#if so put a check here
		current_date = datetime.datetime.now().strftime("%Y-%m-%d")
		job = db.insert('jobs', 
					name=passedData['name']
				)
		
		#Get job info from form and insert into database
		db.update('jobs', where="id = "+str(job), date_started=current_date)
		if 'manager_id' in passedData:
			db.update('jobs', where="id = "+str(job), manager_id=passedData['manager_id'])
		if 'supervisor_id' in passedData:
			db.update('jobs', where="id = "+str(job), supervisor_id=passedData['supervisor_id'])
		if 'customer_name' in passedData:
			db.update('jobs', where="id = "+str(job), customer_name=passedData['customer_name'])
		if 'customer_email' in passedData:
			db.update('jobs', where="id = "+str(job), customer_phone=passedData['customer_phone'])
		if 'customer_name' in passedData:
			db.update('jobs', where="id = "+str(job), customer_email=passedData['customer_email'])
		if 'street_address' in passedData:
			db.update('jobs', where="id = "+str(job), street_address=passedData['street_address'])
		if 'city' in passedData:
			db.update('jobs', where="id = "+str(job), city=passedData['city'])
		if 'state' in passedData:
			db.update('jobs', where="id = "+str(job), state=passedData['state'])
		if 'zip' in passedData:
			db.update('jobs', where="id = "+str(job), zip=passedData['zip'])
		if 'phase' in passedData:
			db.update('jobs', where="id = "+str(job), phase=passedData['phase'])
		if 'budget_available' in passedData:
			db.update('jobs', where="id = "+str(job), budget_available=passedData['budget_available'])
		if 'budget_already_allocated' in passedData:
			db.update('jobs', where="id = "+str(job), budget_already_allocated=passedData['budget_already_allocated'])
		if 'description' in passedData:
			db.update('jobs', where="id = "+str(job), description=passedData['description'])
		return json.dumps(job)
class newUser:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if userIsAdmin(reqUser):
			#user is allowed to do this. 
			#first check if user exists.
			existingUser = db.where('jobAppUsers', email=user)
			if existingUser:
				return "403 Forbidden"
			else: 
				return db.insert('jobAppUsers', 
					name=passedData['name'], 
					email=passedData['email'], 
					phone=passedData['phone'], 
					permissionLevel=passedData['permissionLevel'],
					apiKey=makeNewApiKey()
				)
		else:
			return "403 Forbidden"
class budgetItem:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if reqUser['permissionLevel'].upper() == "ADMIN" or reqUser['permissionLevel'].upper() == "MANAGER":
			#user is allowed to do this. 
			#if passed an id, user wants to update
			if 'id' in passedData:
				try:
					existingItem = db.where('budgetItems', id=int(passedData['id']))[0]
				except:
					#didn't find it. 
					return "404 Not Found"
				if 'name' in passedData:
					db.update('budgetItems', where="id = "+str(existingItem.id), name=passedData['name'])
				if 'cost' in passedData:
					db.update('budgetItems', where="id = "+str(existingItem.id), cost=passedData['cost'])
				if 'type' in passedData:
					db.update('budgetItems', where="id = "+str(existingItem.id), type=passedData['type'])
				return existingItem['id']
			else:
				#no id passed, user wants to add
				newId = db.insert('budgetItems', 
					job_id=int(passedData['job_id']),
					name=passedData['name'],
					cost=passedData['cost'],
					type=passedData['type']
				)
				return json.dumps(newId)				
		else:
			return "403 Forbidden"
class job:
	def GET(self, job):
		#make sure the requestor is a real user
		try:
			apiKey = web.input().apiKey
			reqUser = db.where('jobAppUsers', apiKey=apiKey)[0]
		except:
			return "403 Forbidden"
		if job == "all":
			allJobs = list(db.select('jobs'))
			#make sure the list can be serialized
			for job in allJobs:
				for item in job:
					if type(job[item]) is datetime.date:
						job[item] = str(job[item])
			#then return
			return json.dumps(allJobs)
		else:
			userPrivelege = (reqUser['permissionLevel'].upper() == "ADMIN" or reqUser['permissionLevel'].upper() == "MANAGER")
			theJob = buildJob(job, userPrivelege)
			web.header('Content-Type', 'application/json')
			print theJob
			return theJob
	def POST(self, job):
		#if you're posting here, the job already exists.
		passedData = dict(web.input())
		print passedData
		try:
			apiKey = web.input().apiKey
			reqUser = db.where('jobAppUsers', apiKey=apiKey)[0]
		except:
			return "403 Forbidden"
		try:
			theJob = dict(db.where('jobs', id=job)[0])
		except IndexError:
			return "404 Not Found"
		if 'manager_id' in passedData:
			db.update('jobs', where="id = "+str(job), manager_id=passedData['manager_id'])
		if 'supervisor_id' in passedData:
			db.update('jobs', where="id = "+str(job), supervisor_id=passedData['supervisor_id'])
		if 'customer_name' in passedData:
			db.update('jobs', where="id = "+str(job), customer_name=passedData['customer_name'])
		if 'customer_email' in passedData:
			db.update('jobs', where="id = "+str(job), customer_phone=passedData['customer_phone'])
		if 'customer_name' in passedData:
			db.update('jobs', where="id = "+str(job), customer_email=passedData['customer_email'])
		if 'street_address' in passedData:
			db.update('jobs', where="id = "+str(job), street_address=passedData['street_address'])
		if 'city' in passedData:
			db.update('jobs', where="id = "+str(job), city=passedData['city'])
		if 'state' in passedData:
			db.update('jobs', where="id = "+str(job), state=passedData['state'])
		if 'zip' in passedData:
			db.update('jobs', where="id = "+str(job), zip=passedData['zip'])
		if 'phase' in passedData:
			db.update('jobs', where="id = "+str(job), phase=passedData['phase'])
		if 'budget_available' in passedData:
			db.update('jobs', where="id = "+str(job), budget_available=passedData['budget_available'])
		if 'budget_already_allocated' in passedData:
			db.update('jobs', where="id = "+str(job), budget_already_allocated=passedData['budget_already_allocated'])
		if 'date_started' in passedData:
			db.update('jobs', where="id = "+str(job), date_started=passedData['date_started'])
		if 'date_completed' in passedData:
			db.update('jobs', where="id = "+str(job), date_completed=passedData['date_completed'])
		if 'date_billed' in passedData:
			db.update('jobs', where="id = "+str(job), date_billed=passedData['date_billed'])
		if 'date_closed' in passedData:
			db.update('jobs', where="id = "+str(job), date_closed=passedData['date_closed'])
		if 'description' in passedData:
			db.update('jobs', where="id = "+str(job), description=passedData['description'])
		return "202 Item Updated"	

#Begin Equipment Section
class newEquipment:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if db.where('jobs', name=passedData['name']):
			return "403 Forbidden"
		#are there any people that shouldn't be allowed to create equipment?
		#if so put a check here
		equipment = db.insert('equipment', 
					name=passedData['name']
				)
		
		#Get equipment info from form and insert into database
		if 'category' in passedData:
			db.update('equipment', where="id = "+str(equipment), category=passedData['category'])
		if 'description' in passedData:
			db.update('equipment', where="id = "+str(equipment), description=passedData['description'])
		if 'storage_location' in passedData:
			db.update('equipment', where="id = "+str(equipment), storage_location=passedData['storage_location'])
		
		return "201 Equipment Created"

class equipment:
	def GET(self, equipment):
		#make sure the requestor is a real user
		try:
			apiKey = web.input().apiKey
			reqUser = db.where('jobAppUsers', apiKey=apiKey)[0]
		except:
			return "403 Forbidden"
		allEquipment = list(db.select('equipment'))			
		#then return
		return json.dumps(allEquipment)
	def POST(self, equipment):
		#if you're posting here, the equipment already exists.
		passedData = dict(web.input())
		try:
			apiKey = web.input().apiKey
			reqUser = db.where('jobAppUsers', apiKey=apiKey)[0]
		except:
			return "403 Forbidden"
		try:
			theJob = dict(db.where('equipment', id=passedData['id'])[0])
		except IndexError:
			return "404 Not Found"
		#Get equipment info from form and insert into database
		if 'category' in passedData:
			db.update('equipment', where="id = "+str(equipment), category=passedData['category'])
		if 'description' in passedData:
			db.update('equipment', where="id = "+str(equipment), description=passedData['description'])
		if 'storage_location' in passedData:
			db.update('equipment', where="id = "+str(equipment), storage_location=passedData['storage_location'])
		
		return "201 Equipment Updated"	
		
class deleteEquipment:
	def GET(self): 
		return "Shhhh... the database is sleeping."
	def POST(self):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
		except IndexError:
			return "403 Forbidden"
		if reqUser['permissionLevel'].upper() == "ADMIN" or reqUser['permissionLevel'].upper() == "MANAGER":
			#user can do this
			try:
				theItem = db.where('equipment', id=passedData['id'])[0]
			except:
				return "404 Not Found"
			db.delete('equipment', where="id="+passedData['id'])
			return "200 OK"
		else:
			return "403 Forbidden"

#End Equipment Section		


class user:
	def GET(self, user):
		if user == "all":
			passedData = dict(web.input())
			try:
				reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0]
			except IndexError:
				return "403 Forbidden"
			if userIsAdmin(reqUser):
				#user is allowed to do this
				allUsers = db.select('jobAppUsers', what="id,name,permissionLevel,email,phone")
				web.header('Content-Type', 'application/json')
				return json.dumps(list(allUsers))
			else:
				return "403 Forbidden"
		else:
			try:
				print "Performing lookup on " + user
				print user.isdigit()
				if user.isdigit(): #if all digits, lookup by ID
					return json.dumps(db.where('jobAppUsers', id=user)[0])
				else:
					return json.dumps(db.where('jobAppUsers', email=user)[0])
			except IndexError:
				return "404 Not Found"
	def POST(self, user):
		passedData = dict(web.input())
		try:
			reqUser = db.where('jobAppUsers', apiKey=passedData['apiKey'])[0] 
		except IndexError:
			return "403 Forbidden"
		if userIsAdmin(reqUser):
			#first check if user exists.
			if user.isdigit(): #if all digits, lookup by ID
				existingUser = db.where('jobAppUsers', id=user)
			else:
				existingUser = db.where('jobAppUsers', email=user)
			if existingUser: #user exists
				existingUser = existingUser[0]
				print "*"*50
				print passedData
				print "*"*50
				db.update('jobAppUsers', 
							where="id = "+str(existingUser.id), 
							name=passedData['name'],
							email=passedData['email'],
							permissionLevel=passedData['permissionLevel'],
							phone=passedData['phone']
						)
				return "202 User Updated"
			else: 
				return "404 Not Found"
		else:
			return "403 Forbidden"
def userIsAdmin(user):
	if user['permissionLevel'].upper() == "ADMIN":
		return True
	else:
		return False
def makeNewApiKey():
	potentialApiKey = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(256))
	if len(db.where('jobAppUsers', apiKey=potentialApiKey)) == 0:
		return potentialApiKey
	else:
		return makeNewApiKey()
def buildJob(jobId, isPriveleged):
	try:
		job = dict(db.where('jobs', id=jobId)[0])
	except IndexError:
		return "404 Not Found"

	if isPriveleged:
		#add all priveleged items to the job
		privelegedReferanceThings = [
			['budgetItems', 'budget'],
			['fullEstimates','fullEstimates']
		]
		privelegedIdThings = []
		for thing in privelegedReferanceThings:
			job = addThingByJobReference(job, jobId, thing[0], thing[1])
		for thing in privelegedIdThings:
			job = addThingById(job, thing[0], thing[1])
	#add non-priveleged items to the job
	referanceThings = [
		['notes', 'notes'],
		['dailyReports', 'notes'],
		['actionItems', 'notes'],
		['subContracts','subContracts'],
		['jobContacts','contacts'],
		['maxBudgets','maxBudgets'],
		['equipmentSchedule','equipmentSchedule'],
		['userSchedule','userSchedule'],
		['scopes','scopes'],
		['photoFolders','photoFolders'],
		['photos','photos']
	]
	idThings = [
		['jobAppUsers','manager',job['manager_id'], "name,permissionLevel,email,phone"],
  		['jobAppUsers','supervisor',job['supervisor_id'], "name,permissionLevel,email,phone"],
	]
	for thing in referanceThings:
		theJob = addThingByJobReference(job, jobId, thing[0], thing[1])
	for thing in idThings:
		theJob = addThingById(job, thing[0], thing[1], thing[2], thing[3])
	#sort the list of notes
	job['notes'] = sorted(job['notes'], key=lambda k: k['entry_time'], reverse=True) 
	job = makeDumpable(job)
	return json.dumps(job)
def makeDumpable(inThing):
	if isinstance(inThing, list):
		outThing = []
		for thing in inThing:
			outThing.append(dumpDict(thing))
		return outThing
	else:
		return dumpDict(inThing)
def dumpDict(inDict):
	for item in dict(inDict):
		if type(inDict[item]) is datetime.date or \
			type(inDict[item]) is datetime.datetime:
			inDict[item] = str(inDict[item])
	return inDict
def addThingByJobReference(job, jobId, table, dictName):
	if dictName not in job:
		job[dictName] = []
	things = list(db.where(table, job_id=jobId))
	for thing in things:
		if 'author_id' in thing:
			thing['author'] = list(db.where('jobAppUsers', id=thing['author_id']))[0]
		if 'completion_user' in thing:
			try:
				thing['completion_user'] = list(db.where('jobAppUsers', id=thing['completion_user']))[0]
			except:
				pass
		if 'assigned_user' in thing:
			try:
				thing['assigned_user'] = list(db.where('jobAppUsers', id=thing['assigned_user']))[0]
			except:
				pass
		thing['tbl'] = table
		thing = makeDumpable(thing)
	job[dictName].extend(things)
	return job
def addThingById(job, table, dictName, thingId, what):
	try:
		thing = list(db.where(table, id=thingId, what=what))[0]
	except:
		thing = None
	job[dictName] = thing
	return job


if __name__ == "__main__":
	app.run()
