from flask         import Flask, jsonify, request
from flask_restful import Resource, Api
from inspect       import getmembers, getmodulename, isclass

app = Flask(__name__)
api = Api(app)

from importlib import import_module

class AddResource(Resource):
  def get(self): pass
  def post(self, file):
    path = self.upload_file(file)
    modn = getmodulename(path)
    mod  = import_module(modn, package=None)
    mems = getmembers(mod, lambda m: isinstance(m, Resource))
    for mem in mems:
      rp = f'{modn}.{mem}'
      api.add_resource(rp, mem)
    return path
  def upload_file(self, file):
    return path

# Function to start the DNS server and listen for requests
def start_server(conn):
  api.add_resource(home, '/')
  api.add_resource(disp, '/square/<int:num>')
  app.run(debug = True)


modn = getmodulename('test.py')
print(f'{modn}')
mod  = import_module(modn, package=None)
print(f'{mod}')
mems = getmembers(mod, lambda m: isclass(m) and issubclass(m, Resource) and m is not Resource)
print(f'{mems}')
for mem in mems:
   rp = f'{modn}.{mem}'
   print(f'api.add_resource({rp}, {mem})')

