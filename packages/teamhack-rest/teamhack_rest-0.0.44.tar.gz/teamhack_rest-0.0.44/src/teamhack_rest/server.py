from flask         import Flask, jsonify, request
from flask_restful import Resource, Api
#from teamhack_db.sql import select_hostname_recordtype

app = Flask(__name__)
api = Api(app)

# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
#@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):

		data = "hello world"
		return jsonify({'data': data})


#@app.route('/home/<int:num>', methods = ['GET'])
def disp(num):

	return jsonify({'data': num**2})

#class Hello(Resource):
#  def get(self):
#    return jsonify({'message': 'hello'})
#  def post(self):
#    data = request.get_json()
#    return jsonify({'data': data}), 201
#
#class DNS_C(Resource):
#  def get(self, hostname, record_type, address):
#    pass
#class DNS_R(Resource):
#  def


# Function to start the DNS server and listen for requests
def start_server(conn):
  api.add_resource(home, '/')
  api.add_resource(disp, '/square/<int:num>')
  app.run(debug = True)

