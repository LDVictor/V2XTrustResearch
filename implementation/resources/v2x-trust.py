from flask_restful import Resource, reqparse

elements = [
    'vehicle_01',
    'vehicle_02',
    'vehicle_03',
    'fake_vehicle',
    'ran_01',
    'ran_02'
]

class V2XTrust(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument('msgContent')
    arguments.add_argument('msgEncodeFormat')
    arguments.add_argument('msgType')
    arguments.add_argument('stdOrganization')

