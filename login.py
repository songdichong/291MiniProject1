import sqlite3
from sqlite3 import OperationalError
import re
import hashlib

connection = None
cursor = None

#lab slides
def connect(path):
	global connection, cursor

	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute(' PRAGMA forteign_keys=ON; ')
	connection.commit()
	return
	
#https://stackoverflow.com/questions/19472922/reading-external-sql-script-in-python	
def executeScriptsFromFile(filename):
	# Open and read the file as a single buffer
	fd = open(filename, 'r')
	sqlFile = fd.read()
	fd.close()

	# all SQL commands (split on ';')
	sqlCommands = sqlFile.split(';')

	# Execute every command from the input file
	for command in sqlCommands:
		try:
			cursor.execute(command)
		except OperationalError:
			print("sql create table command error")
			pass
	return

#lab slides
def encrypt(password):
	alg = hashlib.sha256()
	alg.update(password.encode('utf-8'))
	return alg.hexdigest()

def register(cid,name,address,pwd):
	global connection, cursor

	connection.create_function("hash",1,encrypt)
	cursor = connection.cursor()
	data = (cid,name,address,pwd)
	
	cursor.execute("INSERT INTO customers(cid,name,address,pwd) VALUES (?,?,?,hash(?));",data)
	connection.commit()
	return

def checkunique(cid):
	global connection, cursor
	
	cursor.execute("SELECT name from customers c where c.cid = '{0}' UNION SELECT name from agents a where a.aid = '{1}';".format(cid,cid))
	result = cursor.fetchone()
	if result == None:
		return True
	else:
		return False

def c_login(cid, pwd):
	global connection, cursor
	
	connection.create_function("hash",1,encrypt)
	cursor = connection.cursor()
	
	cursor.execute("SELECT * from customers c where c.cid = '{0}' and c.pwd = hash('{1}');".format(cid,pwd))
	result = cursor.fetchone()

	if result == None:
		return False
	else:
		return result

def a_login(aid, pwd):
	global connection, cursor
	
	connection.create_function("hash",1,encrypt)
	cursor = connection.cursor()
	
	cursor.execute("SELECT * from agents a where a.aid = '{0}' and a.pwd = hash('{1}');".format(aid,pwd))
	result = cursor.fetchone()

	if result == None:
		return False
	else:
		return result
	
if __name__=="__main__":
	global connection, cursor
	
	connect('./miniproj1.db')

	executeScriptsFromFile('tables.sql')
	
	while True:
		cmd1 = input("Welcome to mini project1. Do you want to sign up(s) or log in(l)\n")

		if (cmd1 == "s"):
			while True:
				cid = input("please input an id for you: ")
				if (checkunique(cid)==False):
					print ('Sorry, your input id is not unique. Please choose another one')
					continue
					
				name = input("please input a name for you: ")
				address = input("please input an address for you: ")
				pwd = input("please input a password for you: ")
				
				if re.match("^[A-Za-z0-9_]*$", cid) and re.match("^[A-Za-z0-9_]*$", name) and re.match("^[A-Za-z0-9\s]*$", address) and re.match("^[A-Za-z0-9_]*$", pwd):
					register(cid,name,address,pwd)
					cursor.execute("select * from customers;")
					print(cursor.fetchall())
					break
				else:
					print("your input message may be insecure or does not fit general format. Please start again")
					continue
		
		elif (cmd1 == "l"):
			while True:
				cid = input("please input your id: ")
				if checkunique(cid):
					print("your input id does not exists. Please check")
					continue
				pwd = input("please input your password: ")
				
				if (a_login(cid,pwd) != False):
					agent_info = a_login(cid,pwd)
					print("hello, agent {0}.".format(agent_info[1]))
					#things goes on
					
				elif(c_login(cid,pwd) != False):
					customer_info = c_login(cid,pwd)
					print("hello, customer {0}".format(customer_info[1]))
					#things goes on
					
				else:
					print("id and password does not match")
					continue
		elif (cmd1 == "quit"):
			break
	
	
	connection.commit()
	connection.close()
		
