import MySQLdb, string, random, csv, sys, ConfigParser
from datetime import date
from dateutil.rrule import rrule, DAILY




def main():
	config = ConfigParser.ConfigParser()
	config.read("backend.cfg")


	#db access info
	HOST = config.get("Database", "host")
	USER = config.get("Database", "user")
	PASSWD = config.get("Database", "password")
	DATABASE = config.get("Database", "name")
	
	# make a connection to the database
	db_connection = MySQLdb.connect(
	        host=HOST,
	        user=USER, 
	        passwd=PASSWD, 
	        )
	
	#create cursor
	cursor = db_connection.cursor()

	#create our database if it doesn't exist
	try:
		cursor.execute('use '+DATABASE)
	except:
		createDatabase(DATABASE, cursor)
	finally:
		cursor.execute('use '+DATABASE)

	createTables(cursor)
	createTestData(cursor)

	#we're done here. close up shop
	db_connection.commit()
	cursor.close()
	db_connection.close()

def createTables(cursor):
	#create jobs table if it doesn't exist
	if not tblExists("jobs", cursor):
		createJobsTbl(cursor)
	if not tblExists("budgetItems", cursor):
		createBudgetItemsTbl(cursor)
	if not tblExists("dailyReports", cursor):
		createReportsTbl(cursor)
	if not tblExists("actionItems", cursor):
		createActionItemsTbl(cursor)
	if not tblExists("subs", cursor):
		createSubsTbl(cursor)
	if not tblExists("subContracts", cursor):
		createSubContractsTbl(cursor)
	if not tblExists("jobContacts", cursor):
		createJobContactsTbl(cursor)
	if not tblExists("contacts", cursor):
		createContactsTbl(cursor)
	if not tblExists("equipment", cursor):
		createEquipmentTbl(cursor)
	if not tblExists("maxBudgets", cursor):
		createMaxBudgetsTbl(cursor)
	if not tblExists("dates", cursor):
		createDatesTbl(cursor)
	if not tblExists("equipmentSchedule", cursor):
		createEquipmentScheduleTbl(cursor)
	if not tblExists("userSchedule", cursor):
		createUserScheduleTbl(cursor)
	if not tblExists("scopes", cursor):
		createScopesTbl(cursor)
	if not tblExists("fullEstimates", cursor):
		createFullEstimatesTbl(cursor)
	if not tblExists("photos", cursor):
		createPhotosTbl(cursor)
	if not tblExists("photoFolders", cursor):
		createPhotoFoldersTbl(cursor)
	if not tblExists("jobAppUsers", cursor):
		createUsersTbl(cursor)
	if not tblExists("notes", cursor):
		createNotesTbl(cursor)

def createTestData(cursor):
	if tblEmpty("jobAppUsers", cursor):
		createUsers(cursor)
	if tblEmpty("subs", cursor):
		createSubs(cursor)
	if tblEmpty("contacts", cursor):
		createContacts(cursor)
	if tblEmpty("equipment", cursor):
		createEquipment(cursor)
	if tblEmpty("dates", cursor):
		createDates(cursor)
	if tblEmpty("jobs", cursor):
		createJobs(cursor)

	allJobs = []
	cursor.execute('SELECT id FROM jobs')
	for (row_id,) in cursor:
		allJobs.append(row_id)
	allUsers = []
	cursor.execute('SELECT id FROM jobAppUsers')
	for (row_id,) in cursor:
		allUsers.append(row_id)
	allSubs = []
	cursor.execute('SELECT id FROM subs')
	for (row_id,) in cursor:
		allSubs.append(row_id)

	if tblEmpty("budgetItems", cursor):
		createBudgetItems(cursor, allJobs)
	if tblEmpty("dailyReports", cursor):
		createReports(cursor, allJobs, allUsers)
	if tblEmpty("notes", cursor):
		createNotes(cursor, allJobs, allUsers)
	if tblEmpty("actionItems", cursor):
		createActionItems(cursor, allJobs, allUsers)
	if tblEmpty("subContracts", cursor):
		createSubContracts(cursor, allJobs, allSubs)
	if tblEmpty("maxBudgets", cursor):
		createMaxBudgets(cursor, allJobs, allUsers)
	if tblEmpty("scopes", cursor):
		createScopes(cursor, allJobs)
	if tblEmpty("fullEstimates", cursor):
		createFullEstimates(cursor, allJobs)
	if tblEmpty("photoFolders", cursor):
		createPhotoFolders(cursor, allJobs)
	if tblEmpty("photos", cursor):
		createPhotos(cursor, allJobs)

def createDatabase(DATABASE, cursor): 
	#create our database
	print "Creating database: " +DATABASE
	cursor.execute('create database '+DATABASE)

def createJobsTbl(cursor):
	print "Creating table: jobs"
	cursor.execute("""
	CREATE TABLE jobs(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  manager_id INTEGER,
	  supervisor_id INTEGER,
	  customer_id INTEGER,
	  name TEXT(65535),
	  street_address TEXT(65535),
	  city TEXT(65535),
	  state TEXT(65535),
	  zip TEXT(65535),
	  phase TEXT(65535),
	  budget_availiable INTEGER,
	  budget_already_allocated INTEGER,
	  date_started DATE,
	  date_completed DATE,
	  date_billed DATE,
	  date_closed DATE,
	  description TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createBudgetItemsTbl(cursor):
	print "Creating table: budgetItems"
	cursor.execute("""
	CREATE TABLE budgetItems(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER NOT NULL,
	  name TEXT(8000),
	  cost VARCHAR(100),
	  type VARCHAR(100),
	  PRIMARY KEY(id)
	)
	""")
def createNotesTbl(cursor):
	print "Creating table: notes"
	cursor.execute("""
	CREATE TABLE notes(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  author_id INTEGER,
	  entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	  contents TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createUsersTbl(cursor):
	print "Creating table: jobAppUsers"
	cursor.execute("""
	CREATE TABLE jobAppUsers(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  name VARCHAR(255),
	  permissionLevel TEXT(65535),
	  email TEXT(65535),
	  phone VARCHAR(255),
	  apiKey TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createReportsTbl(cursor):
	print "Creating table: dailyReports"
	cursor.execute("""
	CREATE TABLE dailyReports(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  author_id INTEGER,
	  entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	  arrival_time TIMESTAMP,
	  departure_time TIMESTAMP,
	  contents TEXT(65535),
	  people_on_site TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createActionItemsTbl(cursor):
	print "Creating table: actionItems"
	cursor.execute("""
	CREATE TABLE actionItems(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  author_id INTEGER,
	  entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	  completion_time TIMESTAMP,
	  completion_user INTEGER,
	  assigned_user INTEGER,
	  contents TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createSubsTbl(cursor):
	print "Creating table: subs"
	cursor.execute("""
	CREATE TABLE subs(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  company_name TEXT(65535),
	  company_phone TEXT(65535),
	  company_email TEXT(65535),
	  company_fax TEXT(65535),
	  company_address TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createSubContractsTbl(cursor):
	print "Creating table: subContracts"
	cursor.execute("""
	CREATE TABLE subContracts(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  sub_id INTEGER,
	  job_id INTEGER,
	  link TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createJobContactsTbl(cursor):
	print "Creating table: jobContacts"
	cursor.execute("""
	CREATE TABLE jobContacts(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  contact_id INTEGER,
	  job_id INTEGER,
	  role TEXT(65535),
	  description TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createContactsTbl(cursor):
	print "Creating table: contacts"
	cursor.execute("""
	CREATE TABLE contacts(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  company_id INTEGER,
	  name TEXT(65535),
	  phone TEXT(65535),
	  email TEXT(65535),
	  fax TEXT(65535),
	  address TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createEquipmentTbl(cursor):
	print "Creating table: equipment"
	cursor.execute("""
	CREATE TABLE equipment(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  name TEXT(65535),
	  type TEXT(65535),
	  description TEXT(65535),
	  storage_location TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createMaxBudgetsTbl(cursor):
	print "Creating table: maxBudgets"
	cursor.execute("""
	CREATE TABLE maxBudgets(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  author_id INTEGER,
	  entry_time TIMESTAMP,
	  amount TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createDatesTbl(cursor):
	print "Creating table: dates"
	cursor.execute("""
	CREATE TABLE dates(
	  id DATE  NOT NULL,
	  year INTEGER,
	  day_of_week VARCHAR(2),
	  month_number INTEGER,
	  month_name VARCHAR(10),
	  is_holiday BOOLEAN,
	  is_weekend BOOLEAN,
	  PRIMARY KEY(id)
	)
	""")
def createEquipmentScheduleTbl(cursor):
	print "Creating table: equipmentSchedule"
	cursor.execute("""
	CREATE TABLE equipmentSchedule(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  equipment_id INTEGER,
	  job_id INTEGER,
	  full_date DATE,
	  PRIMARY KEY(id)
	)
	""")
def createUserScheduleTbl(cursor):
	print "Creating table: userSchedule"
	cursor.execute("""
	CREATE TABLE userSchedule(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  user_id INTEGER,
	  job_id INTEGER,
	  full_date DATE,
	  PRIMARY KEY(id)
	)
	""")
def createScopesTbl(cursor):
	print "Creating table: scopes"
	cursor.execute("""
	CREATE TABLE scopes(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  link TEXT(65535),
	  upload_time TIMESTAMP,
	  PRIMARY KEY(id)
	)
	""")
def createFullEstimatesTbl(cursor):
	print "Creating table: fullEstimates"
	cursor.execute("""
	CREATE TABLE fullEstimates(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  link TEXT(65535),
	  upload_time TIMESTAMP,
	  PRIMARY KEY(id)
	)
	""")
def createPhotoFoldersTbl(cursor):
	print "Creating table: photoFolders"
	cursor.execute("""
	CREATE TABLE photoFolders(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  parent_id INTEGER,
	  name TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createPhotosTbl(cursor):
	print "Creating table: photos"
	cursor.execute("""
	CREATE TABLE photos(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER,
	  folder_id INTEGER,
	  link TEXT(65535),
	  upload_time TIMESTAMP,
	  PRIMARY KEY(id)
	)
	""")

def createUsers(cursor):
	print "creating data for table: users"
	addUser = """
	INSERT INTO jobAppUsers
		(id, name, permissionLevel, email, apiKey)
    VALUES
    	(NULL, {0}, {1}, {2}, {3})
	"""
	usersToMake = [
		{"name":"Greg","permissionLevel":"Admin","email":"gatlp9@gmail.com"},
		{"name":"Trevor","permissionLevel":"Admin","email":"6573755@gmail.com"},
		{"name":"Tijana","permissionLevel":"Admin","email":"tmilovan@emich.edu"},
		{"name":"Brianna","permissionLevel":"Admin","email":"bwoell@gmail.com"},
		{"name":"Hanna","permissionLevel":"Admin","email":"hjohns25@emich.edu"},
		{"name":"Devon","permissionLevel":"Admin","email":"hawkinsd90@gmail.com"}
	]
	for user in usersToMake:
		apiKey = makeNewApiKey(cursor)
		thisUserAdd = addUser.format(sanitize(user['name']), sanitize(user['permissionLevel']), sanitize(user['email']), sanitize(apiKey))
		cursor.execute(thisUserAdd)
def createSubs(cursor):
	print "creating data for table: subs"
	#company_name TEXT(65535),
	#company_phone TEXT(65535),
	#company_email TEXT(65535),
	#company_fax TEXT(65535),
	#company_address TEXT(65535),
	addThing = """
	INSERT INTO subs
		(id, company_name, company_phone, company_email, company_fax, company_address)
    VALUES
    	(NULL, {0}, {1}, {2}, {3}, {4})
	"""
	thingsToMake = [
		["Dennis's El Cheepo Carpet","877-CASH-NOW","davecarpet@cheepo.net","877-CASH-FAX","123 University Dr, Cupertino CA"],
		["Steve's Carpet","867-CARP-ETT","password@stevecarpet.com","877-CARP-FAX","561 Carpet Rd, Columbia SC"],
		["Frank's Tile","800-YOU-TILE","frankstile@cheepo.net","877-YOU2-FAX","3000 Canada Blvd, Tile TX"]
	]
	for thing in thingsToMake:
		thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]), sanitize(thing[3]), sanitize(thing[4]))
		cursor.execute(thisThingAdd)
def createContacts(cursor):
	print "creating data for table: subs"
	#sub_id INTEGER,
	#name TEXT(65535),
	#phone TEXT(65535),
	#email TEXT(65535),
	#fax TEXT(65535),
	#address TEXT(65535),
	addThing = """
	INSERT INTO contacts
		(id, name, phone, email, fax, address)
    VALUES
    	(NULL, {0}, {1}, {2}, {3}, {4})
	"""
	thingsToMake = [
		["Steve Casa","877-555-5555","fake@example.com","877-555-5555","123 University Dr, Cupertino CA"],
		["Charlie Trailer","877-555-5555","fake@example.com","877-555-5555","561 Carpet Rd, Columbia SC"],
		["Alfie Apartment","877-555-5555","fake@example.com","877-555-5555","3000 Canada Blvd, Tile TX"]
	]
	for thing in thingsToMake:
		thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]), sanitize(thing[3]), sanitize(thing[4]))
		cursor.execute(thisThingAdd)
def createEquipment(cursor):
	print "creating data for table: equipment"
	#name TEXT(65535),
	#type TEXT(65535),
	#description TEXT(65535),
	#storage_location TEXT(65535),
	addThing = """
	INSERT INTO equipment
		(id, name, type, description, storage_location)
    VALUES
    	(NULL, {0}, {1}, {2}, {3})
	"""
	thingsToMake = [
		["Big Fan","Fan","Big and Rusty","Box labeled \"FAN\""],
		["Dehumidifier","Dehumidifier","It's a Dehumidifier","Box labeled \"DEHUMIDIFIER\""],
		["Back Hoe","Back Hoe","It's yellow","The garage"]
	]
	for thing in thingsToMake:
		thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]), sanitize(thing[3]))
		cursor.execute(thisThingAdd)

def createDates(cursor):
	print "creating data for table: dates"
	#id DATE  NOT NULL,
	#year INTEGER,
	#day_of_week VARCHAR(2),
	#month_number INTEGER,
	#month_name VARCHAR(10),
	#is_holiday BOOLEAN,
	#is_weekend BOOLEAN,
	addThing = """
	INSERT INTO dates
		(id)
    VALUES
    	({0})
	"""
	a = date(1900, 1, 1)
	b = date(2100, 12, 31)
	for dt in rrule(DAILY, dtstart=a, until=b):
		thisThingAdd = addThing.format(sanitize(dt.strftime("%Y-%m-%d")))
		cursor.execute(thisThingAdd)
	
def createJobs(cursor):
	print "creating data for table: jobs"
	#id INTEGER  NOT NULL AUTO_INCREMENT,
	#manager_id INTEGER,
	#supervisor_id INTEGER,
	#max_budget_id INTEGER,
	#customer_id INTEGER,
	#name TEXT(65535),
	#street_address TEXT(65535),
	#city TEXT(65535),
	#state TEXT(65535),
	#zip TEXT(65535),
	#phase TEXT(65535),
	#budget_availiable INTEGER,
	#budget_already_allocated INTEGER,
	#date_started DATE,
	#date_completed DATE,
	#date_billed DATE,
	#date_closed DATE,
	#description TEXT(65535),

	addJob = """
	INSERT INTO jobs
		(id, name, street_address, city, state, zip, phase, date_started, description)
	VALUES
		(NULL, {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})
	"""
	jobsToMake = [
		{"name":"Find missing droids", "street_address":"Outskirts", "city":"Mos Eisley", "state":"Tatooine", "zip":"90210", "phase":"open", "date_started":"2015-10-07", "description":"We really need to find these droids"},
		{"name":"Keep an eye on Luke", "street_address":"Moisture Farm", "city":"Desert", "state":"Tatooine", "zip":"90210", "phase":"open", "date_started":"2015-10-06", "description":"What else are you going to do?"},
		{"name":"Shoot First", "street_address":"Chalmun's Cantina", "city":"Mos Eisley", "state":"Tatooine", "zip":"90210", "phase":"open", "date_started":"2015-10-05", "description":"You really weren't looking for any trouble, huh?"},
		{"name":"Collect Jabba's debt", "street_address":"Chalmun's Cantina", "city":"Mos Eisley", "state":"Tatooine", "zip":"90210", "phase":"open", "date_started":"2015-10-04", "description":"Good luck"},
	]
	for job in jobsToMake:
		thisJobAdd = addJob.format(sanitize(job['name']), sanitize(job['street_address']), sanitize(job['city']), sanitize(job['state']), sanitize(job['zip']), sanitize(job['phase']), sanitize(job['date_started']), sanitize(job['description']))
		cursor.execute(thisJobAdd)
def createBudgetItems(cursor, allJobs):
	print "creating data for table: budgetItems"
	#job_id INTEGER NOT NULL,
	#name TEXT(8000),
	#cost VARCHAR(100),
	#type VARCHAR(100),
	addThing = """
	INSERT INTO budgetItems
		(id, job_id, name, cost, type)
    VALUES
    	(NULL, {0}, {1}, {2}, {3})
	"""
	for job in allJobs:
		thingsToMake = [
			[str(job),"Carpet","500","Materials"],
			[str(job),"Carpet Guys","800","Labor"],
			[str(job),"Tile Cleaning","250","Labor"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]), sanitize(thing[3]))
			cursor.execute(thisThingAdd)
def createReports(cursor, allJobs, allUsers):
	print "creating data for table: reports"
	#job_id INTEGER,
	#author_id INTEGER,
	#entry_time TIMESTAMP,
	#arrival_time TIMESTAMP,
	#departure_time TIMESTAMP,
	#contents TEXT(65535),
	#people_on_site TEXT(65535),
	addThing = """
	INSERT INTO dailyReports
		(id, job_id, author_id, entry_time, arrival_time, departure_time, contents, people_on_site)
    VALUES
    	(NULL, {0}, {1}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, {2}, {3})
	"""
	for x in range(0, len(allJobs)):
		thingsToMake = [
			[str(allJobs[x]),str(allUsers[x%len(allUsers)]),"Today we did stuff","Frank, Steve, Dave, Crazy Steve"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]), sanitize(thing[3]))
			cursor.execute(thisThingAdd)
def createNotes(cursor, allJobs, allUsers):
	print "creating data for table: notes"
	#job_id INTEGER,
	#author_id INTEGER,
	#entry_time TIMESTAMP,
	#contents TEXT(65535),
	addThing = """
	INSERT INTO notes
		(id, job_id, author_id, entry_time, contents)
    VALUES
    	(NULL, {0}, {1}, CURRENT_TIMESTAMP, {2})
	"""
	for x in range(0, len(allJobs)):
		thingsToMake = [
			[str(allJobs[x]),str(allUsers[x%len(allUsers)]),"Things are looking good."]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]))
			cursor.execute(thisThingAdd)
def createActionItems(cursor, allJobs, allUsers):
	print "creating data for table: actionItems"
	#job_id INTEGER,
	#author_id INTEGER,
	#entry_time TIMESTAMP,
	#completion_time TIMESTAMP,
	#completion_user INTEGER,
	#assigned_user INTEGER,
	#contents TEXT(65535),
	addThing = """
	INSERT INTO actionItems
		(id, job_id, author_id, entry_time, contents)
    VALUES
    	(NULL, {0}, {1}, CURRENT_TIMESTAMP, {2})
	"""
	for x in range(0, len(allJobs)):
		thingsToMake = [
			[str(allJobs[x]),str(allUsers[x%len(allUsers)]),"We need things for the stuff!"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]))
			cursor.execute(thisThingAdd)
def createSubContracts(cursor, allJobs, allSubs):
	print "creating data for table: subContracts"
	#sub_id INTEGER,
	#job_id INTEGER,
	#link TEXT(65535),
	addThing = """
	INSERT INTO subContracts
		(id, sub_id, job_id, link)
    VALUES
    	(NULL, {0}, {1}, {2})
	"""
	for x in range(0, len(allJobs)):
		thingsToMake = [
			[str(allJobs[x]),str(allSubs[x%len(allSubs)]),"http://example.com"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]))
			cursor.execute(thisThingAdd)
def createMaxBudgets(cursor, allJobs, allUsers):
	print "creating data for table: maxBudgets"
	#job_id INTEGER,
	#author_id INTEGER,
	#entry_time TIMESTAMP,
	#amount TEXT(65535),
	pass
def createScopes(cursor, allJobs):
	print "creating data for table: scopes"
	#job_id INTEGER,
	#link TEXT(65535),
	#upload_time TIMESTAMP,
	addThing = """
	INSERT INTO scopes
		(id, job_id, link, upload_time)
    VALUES
    	(NULL, {0}, {1}, CURRENT_TIMESTAMP)
	"""
	for job in allJobs:
		thingsToMake = [
			[str(job),"http://example.com"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]))
			cursor.execute(thisThingAdd)
def createFullEstimates(cursor, allJobs):
	print "creating data for table: fullEstimates"
	#job_id INTEGER,
	#link TEXT(65535),
	#upload_time TIMESTAMP,
	addThing = """
	INSERT INTO fullEstimates
		(id, job_id, link, upload_time)
    VALUES
    	(NULL, {0}, {1}, CURRENT_TIMESTAMP)
	"""
	for job in allJobs:
		thingsToMake = [
			[str(job),"http://example.com"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]))
			cursor.execute(thisThingAdd)
def createPhotoFolders(cursor, allJobs):
	print "creating data for table: photoFolders"
	#job_id INTEGER,
	#parent_id INTEGER,
	#name TEXT(65535),
	addThing = """
	INSERT INTO photoFolders
		(id, job_id, parent_id, name)
    VALUES
    	(NULL, {0}, {1}, {2})
	"""
	for job in allJobs:
		thingsToMake = [
			[str(job),"0","Temp"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]))
			cursor.execute(thisThingAdd)
def createPhotos(cursor, allJobs):
	print "creating data for table: photos"
	#job_id INTEGER,
	#folder_id INTEGER,
	#link TEXT(65535),
	#upload_time TIMESTAMP,
	addThing = """
	INSERT INTO photos
		(id, job_id, folder_id, link, upload_time)
    VALUES
    	(NULL, {0}, {1}, {2}, CURRENT_TIMESTAMP)
	"""
	for job in allJobs:
		thingsToMake = [
			[str(job),"0","http://www.iana.org/_img/2013.1/icann-logo.svg"]
		]
		for thing in thingsToMake:
			thisThingAdd = addThing.format(sanitize(thing[0]), sanitize(thing[1]), sanitize(thing[2]))
			cursor.execute(thisThingAdd)
def tblExists(name, cursor):
	search_tbl = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = {0}"
	search_tbl = search_tbl.format(sanitize(name))
	cursor.execute(search_tbl)
	if cursor.fetchone()[0] == 1:
		return True
	else:
		return False
def tblEmpty(name, cursor):
	query = """SELECT * from {0} limit 1"""
	entry = cursor.execute(query.format(name))
	if not entry:
		return True
	else:
		return False
def makeNewApiKey(cursor):
	potentialApiKey = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(256))
	query = """SELECT * from jobAppUsers WHERE apiKey={0}"""
	entry = cursor.execute(query.format(sanitize(potentialApiKey)))
	if not entry:
		return potentialApiKey
	else:
		return makeNewApiKey()
def sanitize(inString):
	return "'"+(str(inString).replace("'","\\'").rstrip().lstrip())+"'"

if __name__ == "__main__":
	main()	