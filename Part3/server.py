#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

		python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://hp2414:FHWBZS@w4111db.eastus.cloudapp.azure.com"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#	id serial,
#	name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request

	The variable g is globally accessible
	"""
	try:
		g.conn = engine.connect()
	except:
		print "uh oh, problem connecting to database"
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
	"""

	"""
	# DEBUG: this is debugging code to see what request looks like
	print request.args


	#
	# example of a database query
	#
	cursor = g.conn.execute("SELECT name FROM test")
	names = []
	for result in cursor:
		names.append(result['name'])  # can also be accessed using result[0]
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)
	"""

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#

@app.route('/')
def index():
	return render_template("index.html")


@app.route('/employee')
def employee():
	cursor = g.conn.execute("SELECT * FROM employees")
	names = []
	ids = []
	genders = []
	titles = []
	for result in cursor:
		names.append(result['ename'])
		ids.append(result['eid'])
		genders.append(result['gender'])
		titles.append(result['title'])
	cursor.close()

	cursor = g.conn.execute("SELECT * FROM employees E, manage_aisle M WHERE E.eid = M.eid")
	enames = []
	aids = []
	categories = []
	for result in cursor:
		enames.append(result['ename'])
		aids.append(result['aid'])
		categories.append(result['category'])
	cursor.close()

	context = dict(name = names, id = ids, gender = genders, title = titles, num = len(ids), ename = enames, aid = aids, category = categories, numAisle = len(aids))
	return render_template("employee.html", **context)

@app.route('/addEmployee', methods=['POST'])
def add():
	newName = str(request.form['name'])
	newId = int(request.form['id'])
	newGender = str(request.form['gender'])
	newTitle = str(request.form['title'])
	res = (newTitle , newGender , newId, newName)
	g.conn.execute( "INSERT INTO Employees(title, gender, eid, ename) VALUES (%s, %s, %s, %s)" , res)
	return redirect('/employee')


@app.route('/vip', methods=['POST'])
def vipSearch():
	vid = request.form['vid']
	vid = int(vid)

	cursor = g.conn.execute("SELECT credits FROM vips WHERE vid = %s", vid)
	credits = []
	for result in cursor:
		credits.append(result['credits'])
	cursor.close()

	cursor = g.conn.execute("SELECT * FROM cash_sells CS, credit C WHERE C.sellid = CS.sellid AND C.vid = %s", vid)
	eids = []
	totalPrices = []
	times = []
	sellids = []
	for result in cursor:
		eids.append(result['eid'])
		totalPrices.append(result['totalprice'])
		times.append(result['time'])
		sellids.append(result['sellid'])
	cursor.close()

	context = dict(id = vid, credit = credits[0], eid = eids, totalprice = totalPrices, time = times, sellid = sellids, num = len(eids))
	return render_template("vip.html", **context)

@app.route('/sell', methods=['POST'])
def sellSearch():
	sellid = request.form['id']
	sellid = int(sellid)

	cursor = g.conn.execute("SELECT * FROM apply A, belong_products P WHERE A.sellid = %s AND A.pid = P.pid", sellid)
	quantities = []
	pnames = []
	for result in cursor:
		quantities.append(result['quantity'])
		pnames.append(result['pname'])
	cursor.close()

	cursor = g.conn.execute("SELECT totalprice, time FROM cash_sells C WHERE C.sellid = %s", sellid)
	totalprice = []
	time = []
	for result in cursor:
		totalprice.append(result['totalprice'])
		time.append(result['time'])
	cursor.close()

	context = dict(id = sellid, price = totalprice[0], time = time[0], quantity = quantities, pname = pnames, num = len(pnames))
	return render_template("sell.html", **context)


@app.route('/customer')
def cc():
	return render_template("customer.html")

@app.route('/productname', methods=['POST'])
def productsearch():
	pname_in = request.form['produ']
	#cursor = g.conn.execute("SELECT * FROM belong_products B, provide P  where B.pid = P.pid AND B.pname = %s", pname_in)
	cursor = g.conn.execute("SELECT * FROM (SELECT B.pname, B.price, B.aid, P.sname, B.pid FROM belong_products B, provide P  where B.pid = P.pid AND B.pname = %s) A LEFT OUTER JOIN have H on A.pid = H.pid", pname_in)
	prices1 = []
	pnames1 = []
	aisles1 = []
	snames1 = []
	promotionnames1 = []
	for result in cursor:
		pnames1.append(result['pname'])
		prices1.append(result['price'])
		aisles1.append(result['aid'])
		snames1.append(result['sname'])
		promotionnames1.append(result['promotionname'])
	cursor.close()

	context = dict(pname_in = pname_in, prices = prices1, pnames = pnames1, aisles = aisles1, snames=snames1, num = len(pnames1), promotionnames1 = promotionnames1)

	return render_template("product.html", **context)


@app.route('/category', methods=['POST'])
def categorysearch():
	category_in = request.form['categ']
	cursor = g.conn.execute("SELECT * FROM belong_products B, manage_aisle M  where B.aid = M.aid and M.category = %s", category_in)
	aids2 = []
	pnames2 = []
	prices2 = []
	for result in cursor:
		aids2.append(result['aid'])
		pnames2.append(result['pname'])
		prices2.append(result['price'])
	cursor.close()
	context  = dict(category_in = category_in, aids2 = aids2, pnames2 = pnames2, prices2 = prices2, num = len(aids2), category = category_in)
	return render_template("category.html", **context)


@app.route('/promotion', methods=['POST'])
def promotionsearch():
	name_in = request.form['promo']
	cursor = g.conn.execute("SELECT * From provide PV, promotion P, have H, belong_products BP where PV.pid = BP.pid AND H.promotionname = P.promotionname AND H.pid = BP.pid AND P.promotionname = %s", name_in)
	discounts3 = []
	stimes3 = []
	etimes3 = []
	pnames3 = []
	prices3 = []
	snames3 = []
	for result in cursor:
		discounts3.append(result['discount'])
		pnames3.append(result['pname'])
		stimes3.append(result['starttime'])
		etimes3.append(result['endtime'])
		prices3.append(result['price'])
		snames3.append(result['sname'])
	cursor.close()
	context = dict(name_in = name_in, discounts3 = discounts3, stimes3= stimes3, etimes3 = etimes3,pnames3 = pnames3, prices3 = prices3, num = len(pnames3), name = name_in, snames3 = snames3)
	return render_template("promotion.html", **context)


@app.route('/datepromotion', methods=['POST'])
def datepromotionsearch():
	date_in = request.form['date']
	cursor = g.conn.execute("SELECT * FROM provide PV, belong_products PR, Have H, Promotion P1 WHERE PV.pid = PR.pid AND PR.pid = H.pid AND P1.promotionname = H.promotionname AND H.promotionname IN (SELECT P.promotionname FROM promotion P WHERE %s - P.starttime >= 0 AND P.endtime - %s >= 0);", date_in,date_in)
	discounts3 = []
	stimes3 = []
	etimes3 = []
	pnames3 = []
	prices3 = []
	snames3 = []
	promotionnames3 = []
	for result in cursor:
		discounts3.append(result['discount'])
		pnames3.append(result['pname'])
		stimes3.append(result['starttime'])
		etimes3.append(result['endtime'])
		prices3.append(result['price'])
		snames3.append(result['sname'])
		promotionnames3.append(result['promotionname'])
	cursor.close()
	context = dict(date_in = date_in, discounts3 = discounts3, stimes3= stimes3, etimes3 = etimes3, pnames3 = pnames3, prices3 = prices3, num = len(pnames3), date = date_in, snames3 = snames3, promotionnames3 = promotionnames3)
	return render_template("datepromotion.html", **context)







# Example of adding new data to the database
'''
@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
	return redirect('/')
'''


@app.route('/login')
def login():
		abort(401)
		this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using

				python server.py

		Show the help text using

				python server.py --help

		"""

		HOST, PORT = host, port
		print "running on %s:%d" % (HOST, PORT)
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


	run()
