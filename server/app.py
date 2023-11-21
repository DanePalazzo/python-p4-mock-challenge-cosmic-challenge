#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, abort
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(rules=("-missions",)) for scientist in Scientist.query.all()]
        return scientists, 200

    def post(self):
        try:
            scientist = Scientist(
                name = request.json["name"],
                field_of_study = request.json["field_of_study"],
            )
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 200
        except:
            return {"errors": ["validation errors"]}, 400

class ScientistByID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        scientist_dict = scientist.to_dict()
        return scientist_dict, 200

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        data = request.get_json()
        for key in data:
            try:
                setattr(scientist, key, data[key])
            except:
                return {"errors": ["validation errors"]}, 400
        db.session.add(scientist)
        db.session.commit()
        return scientist.to_dict(), 202
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        db.session.delete(scientist)
        db.session.commit()
        return {}, 204
    
class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=("-missions",)) for planet in Planet.query.all()]
        return planets, 200

class Missions(Resource):
    def get(self):
        missions = [mission.to_dict() for mission in Mission.query.all()]
        return missions, 200
    
    def post(self):
        try:
            mission = Mission(
                name = request.json["name"],
                scientist_id = request.json["scientist_id"],
                planet_id = request.json["planet_id"],
                )
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Missions, "/missions")
api.add_resource(Planets, "/planets")
api.add_resource(Scientists, "/scientists")
api.add_resource(ScientistByID, "/scientists/<int:id>")

@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
