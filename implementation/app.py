from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

api.add_resource(V2XTrust)

if __name__ == '__main__':
    app.run(debug=True)

# preciso iniciar o v2x-trust aqui
