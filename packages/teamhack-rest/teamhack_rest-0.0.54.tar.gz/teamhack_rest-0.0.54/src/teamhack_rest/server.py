from flask         import Flask, jsonify, request
from flask_restful import Resource, Api
from importlib     import import_module
from inspect       import getmembers, getmodulename
from tempfile      import NamedTemporaryFile
#from teamhack_db.sql import select_hostname_recordtype

app = Flask(__name__)
api = Api(app)

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


class AddResource(Resource):
  def get(self, file): pass

  def post(self, file):
    path = self.upload_file(file)
    modn = getmodulename(path)
    mod  = import_module(modn, package=None)
    mems = getmembers(mod, self.predicate)
    for mem in mems:
      rp = f'{modn}.{mem}'
      api.add_resource(rp, mem)
    return jsonify({'name': modn})

  def predicate(self, m):
    if not isclass(m):              return False # guard following checks from exceptions
    if m is Resource:               return False # skip non-subclass
    if not issubclass(m, Resource): return False # check for subclass
    return True

  def upload_file(self, file):
    path = tempfile.NamedTemporaryFile(delete=False)
    path.write(file)
    return path

# Function to start the DNS server and listen for requests
def start_server(conn):
  api.add_resource(AddResource, '/teamhack_db.server.AddResource/<string:file>')
  app.run(debug=True)

