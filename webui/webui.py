import web, ConfigParser, json, sys, urllib, requests, tempfile
from os import path
from identitytoolkit import gitkitclient

#read the config file
config = ConfigParser.ConfigParser()
root = path.dirname(path.realpath(__file__))
config.read(path.join(root, "webui.cfg"))

#gitkit_config_json = config.get("Google", "GitkitJSON")
gitkit_config_json = path.join(root, config.get("Google", "GitkitJSON"))
gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(gitkit_config_json)

web.config.debug = True
debug = False

urls = (
	"/", "index",
	"/login", "login",
	"/logout", "logout",
	"/dashboard", "dashboard",
	"/update", "update",
	"/admin","admin"
	)
render = web.template.render(path.join(root,'templates/'))
app = web.application(urls, globals())

apiUrl = config.get("Backend", "url")

# Hack to make session play nice with the reloader (in debug mode)
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore(path.join(root,'sessions')), initializer={'user': {'state':None, 'isAdmin':0}})
    web.config._session = session
else:
    session = web.config._session

class index:
	def GET(self):
		gtoken = web.cookies().get('gtoken')
		if gtoken is not None:
			gVars = vars(gitkit_instance.VerifyGitkitToken(gtoken))
			if not session.user.has_key('isInTable'):
				if session.user['state'] != 'unregistered':
					session.user = makeUserSession(gVars)
		else:
			session.user['state'] = None

		if session.user['state'] == "registered":
			if session.user.has_key('redirect'):
				raise web.seeother(session.user['redirect'])
			else:
				raise web.seeother('dashboard')
		elif session.user['state'] == "unregistered":
			text = "You have logged in with Google, but are not a member of this company. Please contact your administrator if you feel you need access" 
			if debug:
				text += ".... here is your session info: " + str(session.user)
			title = "Are you sure you work here?"
			return render.unregistered(title, text)
		elif session.user['state'] == None:
			text = "" 
			if debug:
				text += "Here is your session info: "  + str(session.user)
			title = "Welcome, Stranger!"
			return render.unauthed(title, text)
		else:
			text = "Strange error. Contact an admin." 
			if debug:
				text += "Here is your session info: "  + str(session.user)
			title = "Wait.. what?"
			return render.index(title, text)
			



class login:
	def GET(self):
		return render.login()

class logout:
	def GET(self):
		session.user = {'state':None, 'isAdmin':0}
		raise web.seeother('/')
class dashboard:
	def GET(self):
		if not userAuthed(session.user):
			session.user['redirect'] = web.ctx.path
			raise web.seeother('/')
		text = "You are a registered user "
		adminLink = " "
		if session.user['isAdmin']:
			text += "and an admin.. People respect you "
			adminLink += "<a href=\"admin\" class=\"adminButton\">Admin Panel</a>"
		if debug:
			text += "..... here is your session info: " + str(session.user)
		title = "Welcome back, " + session.user['name'] + "!" 
		return render.dashboard(title, text, adminLink)
class admin:
	form = web.form.Form(
		web.form.Textbox('email',
            size=30,
            description="Google Account:"),
        web.form.Textbox('name', web.form.notnull, 
            size=30,
            description="User's Name:"),
        web.form.Textbox('title',
            size=30,
            description="Job Title:"),
        web.form.Checkbox('isAdmin',
        	description="Is User an Admin?"),
        web.form.Button('Add/Update User'),
    )

	def GET(self):
		if not userAuthed(session.user) or not userIsAdmin(session.user):
			raise web.seeother('/')
		if session.user.has_key('apiResponse'):
			response = session.user['apiResponse']
			del session.user['apiResponse']
		else:
			response = ""
		return render.admin(response, self.form)
	def POST(self):
		form = self.form()
		if not form.validates():
			return render.admin("Form validation failed", self.form)
		user_form = dict(form.d)
		print "user_form['isAdmin'] = " + str(user_form['isAdmin']) + "\n type: " + str(type(user_form['isAdmin']))
		if user_form['isAdmin'] == True:
			user_form['isAdmin'] = "True"
		else:
			user_form['isAdmin'] = "False"
		print "user_form['isAdmin'] = " + str(user_form['isAdmin']) + "\n type: " + str(type(user_form['isAdmin']))
		user_form['apiKey'] = session.user['apiKey']
		apiRequest = requests.post(apiUrl+"/user/"+user_form['email'], data=user_form)
		session.user['apiResponse'] = apiRequest.text
		user_form = {}
		raise web.seeother('/admin')

class update:
	form = web.form.Form(
        web.form.Checkbox('acknowledge',
        	description="You're sure you want to update right now?",
        	value="acknowledged"),
        web.form.Button('Do the Update!'),
    )
	def GET(self):
		text = "While updating the site will be unavailiable to you and your project mates for up to a minute. Are you sure now is a good time?"
                return render.text_form(text, self.form)		

def userIsAdmin(user):
	if user['isAdmin']:
		return True
	else:
		return False
def userAuthed(user):
	if user.has_key('isInTable'):
		return True
	else:
		return False

def makeUserSession(gVars):
	session = gVars
	session['state'] = "unregistered"
	#try to ask backend for this user's info
	response = urllib.urlopen(apiUrl+"/user/"+gVars['email']).read()
	if response[0:3] != '404':
		session.update(dict(json.loads(response)))
		session['state'] = "registered"
	return session

if __name__ == "__main__":
	app.run()
