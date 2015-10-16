import web, ConfigParser, json, string, random, socket, urllib
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
	)

app = web.application(urls, globals())
db = web.database(dbn='mysql', host=config.get("Database", "host"), port=int(config.get("Database", "port")), user=config.get("Database", "user"), pw=config.get("Database", "password"), db=config.get("Database", "name"))
def set_headers():
    web.header('Access-Control-Allow-Origin',      '*')
app.add_processor(web.loadhook(set_headers))

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
			if passedData['isAdmin'].lower() == u'true':
				passedData['isAdmin'] = 1
			else:
				passedData['isAdmin'] = 0
			if passedData['canSeeNumbers'].lower() == u'true':
				passedData['canSeeNumbers'] = 1
			else:
				passedData['canSeeNumbers'] = 0
			#first check if user exists.
			existingUser = db.where('jobAppUsers', email=user)
			if existingUser:
				return "403 Forbidden"
			else: 
				return db.insert('jobAppUsers', 
					name=passedData['name'], 
					email=passedData['email'], 
					title=passedData['title'], 
					isAdmin=passedData['isAdmin'],
					canSeeNumbers=passedData['canSeeNumbers'], 
					isInTable=1,
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
			return json.dumps(list(db.select('jobs')))
		else:
			try:
				theJob = dict(db.where('jobs', id=job)[0])
			except IndexError:
				return "404 Not Found"
			if reqUser['canSeeNumbers']:
				try:
					jobsBugetItems = list(db.where('budgetItems', job_id=job))
					#force an exception if there are no budget items
					jobsBugetItems[0]
					if not reqUser['canSeeNumbers']:
						pass
						#todo remove numbers for those not allowed to see them
					theJob['budget'] = jobsBugetItems
				except IndexError:
					pass
					#jobs are allowed to not have budgets
			web.header('Content-Type', 'application/json')
			return json.dumps(theJob)
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
				allUsers = db.select('jobAppUsers', what="id,name,permissionLevel,phone")
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
			#user is allowed to do this. 
			if passedData['isAdmin'] == u'True':
				passedData['isAdmin'] = 1
			else:
				passedData['isAdmin'] = 0
			if passedData['canSeeNumbers'] == u'True':
				passedData['canSeeNumbers'] = 1
			else:
				passedData['canSeeNumbers'] = 0
			#first check if user exists.
			if user.isdigit(): #if all digits, lookup by ID
				existingUser = db.where('jobAppUsers', id=user)
			else:
				existingUser = db.where('jobAppUsers', email=user)
			if existingUser: #user exists
				existingUser = existingUser[0]
				db.update('jobAppUsers', 
							where="id = "+str(existingUser.id), 
							name=passedData['name'],
							email=passedData['email'],
							title=passedData['title'],
							isAdmin=passedData['isAdmin'],
							canSeeNumbers=passedData['canSeeNumbers']
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
if __name__ == "__main__":
	app.run()
