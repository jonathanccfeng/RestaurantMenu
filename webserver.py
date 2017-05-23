from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer, SocketServer
import cgi
import time


from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		try:
			if self.path.endswith('/restaurants'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				
				listRestaurants = session.query(Restaurant).order_by(Restaurant.name.asc()).all()
				
				output = ''
				output += '<html><body>'
				output += '<h1>List of Restaurants</h1>'
				for restaurant in listRestaurants:
					output += '<p>%s</br>' % restaurant.name
					output += '<a href="/restaurants/%s/edit">Edit</a></br>' % restaurant.id
					output += '<a href="/restaurants/%s/delete">Delete</a></br>' % restaurant.id
					output += '</p>'

				output += '<h3><a href="/restaurants/new">Create a new restaurant</a></h3>'
				output += '</body></html>'
				self.wfile.write(output)
				#print output
				return

			if self.path.endswith('/restaurants/new'):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ''
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
				output += '<h2>Make a New Restraurant</h2>&nbsp;<input name="newRestaurantName" type="text" >'
				output += '<input type="submit" value="Create"> </form>'
				
				self.wfile.write(output)
				#print output
				return
			if self.path.endswith('/edit'):
				restaurantId = self.path.split("/")[2]
				restaurantQuery = session.query(Restaurant).filter_by(id = restaurantId).one()

				if restaurantQuery:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = '<html><body>'
					output += '<h1>%s</h1>' % restaurantQuery.name
					output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantId
					output += '<input name = "newRestaurantName" type="text" placeholder = "%s" >' % restaurantQuery.name
					output += "<input type = 'submit' value = 'Rename'>"
					output += "</form>"
					output += "</body></html>" 
					self.wfile.write(output)
			if self.path.endswith('/delete'):
				restaurantId = self.path.split("/")[2]
				restaurantQuery = session.query(Restaurant).filter_by(id = restaurantId).one()

				if restaurantQuery:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = '<html><body>'

					output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/delete' >" % restaurantId
					output += "<h3>Are you sure you want to delete '%s'?</h3>" % restaurantQuery.name
					output += "<input type = 'submit' value = 'Delete'>"
					output += "</form>"

					output += "<button onclick='history.go(-1);return true;'>Go Back</button>"
					output += "</body></html>" 
					self.wfile.write(output)

					#session.delete(restaurantQuery)
					#session.commit()

		except IOError:
			self.send_error(404, 'File Not Found %s' % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')

                    # Create new Restaurant Object
					newRestaurant = Restaurant(name=messagecontent[0])
					session.add(newRestaurant)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messageContent = fields.get('newRestaurantName')
					restaurantId = self.path.split("/")[2]

					restaurantQuery = session.query(Restaurant).filter_by(id = restaurantId).one()

					if restaurantQuery != []:
						restaurantQuery.name = messageContent[0]
						session.add(restaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()
			if self.path.endswith("/delete"):

				if ctype == 'multipart/form-data':
					restaurantId = self.path.split("/")[2]
					restaurantQuery = session.query(Restaurant).filter_by(id = restaurantId).one()

					if restaurantQuery:
						session.delete(restaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()       

		except:
			pass


def main():
	try:
		port = 8000
		server = HTTPServer(('',port), webserverHandler)
		print 'Web server running on port %s' % port
		server.socket.settimeout(10)
		server.handle_request()
		#server.serve_forever()



	except KeyboardInterrupt:
		print '^C entered, stopping web server...'
		server.socket.close()





if __name__ == '__main__':
	main()