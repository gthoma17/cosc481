import MySQLdb, string, random, csv, sys, ConfigParser




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

	#create jobsobs table if it doesn't exist
	if not tblExists("jobs", cursor):
		createJobsTbl(cursor)
	#create users table if it doesn't exist
	#if not tblExists("budgets", cursor):
	#	createBudgetsTbl(cursor)
	if not tblExists("budgetItems", cursor):
		createBudgetItemsTbl(cursor)
	#if not tblExists("budgetItemCosts", cursor):
	#	createBudgetItemCostsTbl(cursor)
	if not tblExists("comments", cursor):
		createCommentsTbl(cursor)
	if not tblExists("jobAppUsers", cursor):
		createUsersTbl(cursor)
	#add some users
	if tblEmpty("jobAppUsers", cursor):
		createUsers(cursor)
	#add some jobs so things aren't so empty
	if tblEmpty("jobs", cursor):
		createJobs(cursor)
	#we're done here. close up shop
	db_connection.commit()
	cursor.close()
	db_connection.close()

def createDatabase(DATABASE, cursor): 
	#create our database
	print "Creating database: " +DATABASE
	cursor.execute('create database '+DATABASE)

def createJobsTbl(cursor):
	print "Creating table: jobs"
	cursor.execute("""
	CREATE TABLE jobs(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  name TEXT(8000),
	  location TEXT(8000),
	  bill_to TEXT(8000),
	  poc_phone VARCHAR(100),
	  date_started VARCHAR(100),
	  date_completed VARCHAR(100),
	  date_billed VARCHAR(100),
	  description TEXT(65535),
	  isInProgress BOOLEAN,
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
def createCommentsTbl(cursor):
	print "Creating table: comments"
	cursor.execute("""
	CREATE TABLE comments(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  job_id INTEGER NOT NULL,
	  time TIMESTAMP,
	  postedBy VARCHAR(255),
	  comment TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createUsersTbl(cursor):
	print "Creating table: jobAppUsers"
	cursor.execute("""
	CREATE TABLE jobAppUsers(
	  id INTEGER  NOT NULL AUTO_INCREMENT,
	  name VARCHAR(255),
	  title TEXT(65535),
	  email TEXT(65535) NOT NULL,
	  canSeeNumbers BOOLEAN,
	  isInTable BOOLEAN,
	  isAdmin BOOLEAN,
	  apiKey TEXT(256),
	  googId TEXT(65535),
	  PRIMARY KEY(id)
	)
	""")
def createUsers(cursor):
	addUser = """
	INSERT INTO jobAppUsers
		(id, name, title, email, isInTable, isAdmin, canSeeNumbers, apiKey)
    VALUES
    	(NULL, {0}, {1}, {2}, 1, 1, 1, {3})
	"""
	usersToMake = [
		{"name":"Greg","title":"SWE","email":"gatlp9@gmail.com"},
		{"name":"Trevor","title":"Some sort of manager thing","email":"6573755@gmail.com"},
		{"name":"Tijana","title":"SWE","email":"tmilovan@emich.edu"},
		{"name":"Brianna","title":"SWE","email":"bwoell@gmail.com"},
		{"name":"Hanna","title":"SWE","email":"hjohns25@emich.edu"},
		{"name":"Devon","title":"SWE","email":"hawkinsd90@gmail.com"}
	]
	for user in usersToMake:
		apiKey = makeNewApiKey(cursor)
		thisUserAdd = addUser.format(sanitize(user['name']), sanitize(user['title']), sanitize(user['email']), sanitize(apiKey))
		cursor.execute(thisUserAdd)
def createJobs(cursor):
	addJob = """
	INSERT INTO jobs
		(id, name, location, bill_to, poc_phone, description, isInProgress)
	VALUES
		(NULL, {0}, {1}, {2}, {3}, {4}, {5})
	"""
	jobsToMake = [
		{"name":"Find missing droids", "location":"Mos Eisley", "bill_to":"Imperial Army", "poc_phone":"1800DARKSID", "description":"We really need to find these droids","isInProgress":1},
		{"name":"Keep an eye on Luke", "location":"Tatooine", "bill_to":"Obi Wan Kenobi", "poc_phone":"1734GETJEDI", "description":"What else are you going to do?","isInProgress":0},
		{"name":"Shoot First", "location":"Chalmun's Cantina", "bill_to":"Han Solo", "poc_phone":"1877SHIPFAST", "description":"You really weren't looking for any trouble, huh?","isInProgress":1},
		{"name":"Collect Jabba's debt", "location":"Chalmun's Cantina", "bill_to":"Greedo", "poc_phone":"18554OUCHIE", "description":"Good luck","isInProgress":1},
	]
	for job in jobsToMake:
		thisJobAdd = addJob.format(sanitize(job['name']), sanitize(job['location']), sanitize(job['bill_to']), sanitize(job['poc_phone']), sanitize(job['description']), sanitize(job['isInProgress']))
		cursor.execute(thisJobAdd)
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