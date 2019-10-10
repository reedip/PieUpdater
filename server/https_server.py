import constants
from flask import Flask
from flask import render_template
from flask import request
from flask_restful import Api, Resource
app = Flask(__name__)
api = Api(app)

def uploadPackage():
    return True

def getPackageInfo(*args):
    return args

# app.route creates the URI endpoint for flask
# reference:https://www.youtube.com/watch?v=s_ht4AKnWZg
class HomePage(Resource):
    def get(self):
        return {'about': "Welcome to %s. Please visit the correct URI "
                "for further processing." % constants.COMPANY_NAME}

class Packages(Resource):
    def post(self):
        return {'Package Upload': uploadPackage()}

    def get(self, num):
        return {'Package Information': getPackageInfo(num)}

class UploadPackage(Resource):
    '''
    def __init__(self, *args):
        print(str(args))
    '''

    def post(self):
        file = request.files['file']
        print("Here right now")
        return ("Saved the file :%s" % file.filename)

    def options(self):
        print("Here right now")

api.add_resource(HomePage, "/")
api.add_resource(Packages, "/packages/")
api.add_resource(UploadPackage, "/packages/upload/", endpoint='uploadpackage')

if __name__ == '__main__':
    app.run(ssl_context=(constants.SERVER_CERT, constants.SERVER_KEY),
            debug=constants.DEBUG)
    # Reference: https://blog.miguelgrinberg.com/post/
    # running-your-flask-application-over-https
