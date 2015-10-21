import web, ConfigParser, json, string, random, socket, urllib, datetime
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
	"/job", "newJob",
	"/job/(.*)", "job",
	"/budgetItem", "budgetItem",
	"/note", "note",
	"/actionItem/(.*)", "actionItem",
	)

app = web.application(urls, globals())
db = web.database(dbn='mysql', host=config.get("Database", "host"), port=int(config.get("Database", "port")), user=config.get("Database", "user"), pw=config.get("Database", "password"), db=config.get("Database", "name"))
def set_headers():
    web.header('Access-Control-Allow-Origin',      '*')
app.add_processor(web.loadhook(set_headers))

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
		if db.where('jobs', name=passedData['name']):
			return "403 Forbidden"
		if "assigned_user" in passedData:
			db.update(tbl, where="id = "+str(passedData['note_id']), 
					assigned_user=passedData['assigned_user']
				)
		if "completion_user" in passedData:
			db.update(tbl, where="id = "+str(passedData['note_id']), 
					completion_user=passedData['arrival_time']
					completion_time="CURRENT_TIMESTAMP"
				)
		return "202 Note Updated"

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
		if db.where('jobs', name=passedData['name']):
			return "403 Forbidden"
		tbl = passedData['tbl']
		note = db.insert(tbl, 
					job_id=passedData['job_id'],
					author_id=passedData['author_id'],
					contents=passedData['contents']
				)
		if tbl == "dailyReports":
			db.update(tbl, where="id = "+str(note), 
					arrival_time=passedData['arrival_time']
					departure_time=passedData['departure_time']
					people_on_site=passedData['people_on_site']
				)
		if tbl == "actionItems" and "assigned_user" in passedData:
			db.update(tbl, where="id = "+str(note), 
					assigned_user=passedData['assigned_user']
				)
		return "201 Note Created"

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
		job = db.insert('jobs', 
					name=passedData['name']
				)
		if passedData['isInProgress'] == u'True':
			passedData['isInProgress'] = 1
		else:
			passedData['isInProgress'] = 0
		if 'location' in passedData:
			db.update('jobs', where="id = "+str(job), location=passedData['location'])
		if 'date_started' in passedData:
			db.update('jobs', where="id = "+str(job), date_started=passedData['date_started'])
		if 'date_completed' in passedData:
			db.update('jobs', where="id = "+str(job), date_completed=passedData['date_completed'])
		if 'date_billed' in passedData:
			db.update('jobs', where="id = "+str(job), date_billed=passedData['date_billed'])
		if 'bill_to' in passedData:
			db.update('jobs', where="id = "+str(job), bill_to=passedData['bill_to'])
		if 'description' in passedData:
			db.update('jobs', where="id = "+str(job), description=passedData['description'])
		if 'isInProgress' in passedData:
			db.update('jobs', where="id = "+str(job), isInProgress=passedData['isInProgress'])
		return "201 Job Created"
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
		if reqUser['canSeeNumbers']:
			#user is allowed to do this. 
			#update if an identical budget item exists
			existingItem = db.where('budgetItems', 
							job_id=int(passedData['job_id']),
							name=passedData['name'],
							type=passedData['type']
						)
			if not existingItem:
				#item wasn't in database
				newId = db.insert('budgetItems', 
					job_id=int(passedData['job_id']),
					name=passedData['name'],
					cost=passedData['cost'],
					type=passedData['type']
				)
				return json.dumps(newId)
			else:
				#update existing item
				existingItem = existingItem[0]
				if 'name' in passedData:
					db.update('budgetItems', where="id = "+str(existingItem.id), name=passedData['name'])
				if 'cost' in passedData:
					db.update('budgetItems', where="id = "+str(existingItem.id), cost=passedData['cost'])
				if 'type' in passedData:
					db.update('budgetItems', where="id = "+str(existingItem.id), type=passedData['type'])
				return existingItem['id']
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
		if 'name' in passedData:
			db.update('jobs', where="id = "+str(job), name=passedData['name'])
		if 'location' in passedData:
			db.update('jobs', where="id = "+str(job), location=passedData['location'])
		if 'date_started' in passedData:
			db.update('jobs', where="id = "+str(job), date_started=passedData['date_started'])
		if 'date_completed' in passedData:
			db.update('jobs', where="id = "+str(job), date_completed=passedData['date_completed'])
		if 'date_billed' in passedData:
			db.update('jobs', where="id = "+str(job), date_billed=passedData['date_billed'])
		if 'bill_to' in passedData:
			db.update('jobs', where="id = "+str(job), bill_to=passedData['bill_to'])
		if 'description' in passedData:
			db.update('jobs', where="id = "+str(job), description=passedData['description'])
		if 'isInProgress' in passedData:
			db.update('jobs', where="id = "+str(job), isInProgress=passedData['isInProgress'])
		return "202 Item Updated"	
		


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
  		['contacts','customer',job['customer_id'], "*"]
	]
	for thing in referanceThings:
		theJob = addThingByJobReference(job, jobId, thing[0], thing[1])
	for thing in idThings:
		theJob = addThingById(job, thing[0], thing[1], thing[2], thing[3])
	job = makeDumpable(job)
	print "*"*50
	print job
	print "*"*50
	return json.dumps(job)
def makeDumpable(inDict):
	for item in inDict:
		if type(inDict[item]) is datetime.date or \
			type(inDict[item]) is datetime.datetime:
			inDict[item] = str(inDict[item])
	return inDict
def addThingByJobReference(job, jobId, table, dictName):
	if dictName not in job:
		job[dictName] = []
	things = list(db.where(table, job_id=jobId))
	for thing in things:
		thing['tbl'] = table
		thing = makeDumpable(thing)
	job[dictName].append(things)
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
