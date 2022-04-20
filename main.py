from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
from marshmallow import Schema, post_load, ValidationError, validates, validate
import marshmallow
from sqlalchemy import or_
from flask_cors import CORS, cross_origin


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Pass123@localhost/rest_api_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
cors = CORS(app)
# ma = Marshmallow(app)

class VideoModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), nullable=False)
	views = db.Column(db.Integer, nullable=False)
	likes = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"Video(name = {name}, views = {views}, likes = {likes}"

class RandomLoader(db.Model):
	__tablename__ = 'random_loader'
	id = db.Column(db.Integer, primary_key=True)
	col1 = db.Column(db.String)
	col2 = db.Column(db.String)
	col3 = db.Column(db.String)
	col4 = db.Column(db.String)
	col5 = db.Column(db.String)
	col6 = db.Column(db.String)

resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'views': fields.Integer,
	'likes': fields.Integer
}

random_fields = {
	'id': fields.Integer,
	'col1': fields.String,
	'col2': fields.String,
	'col3': fields.String,
	'col4': fields.String,
	'col5': fields.String,
	'col6': fields.String,
}


class VideoSchema(Schema):
    name = marshmallow.fields.String(validate=validate.Length(max=5), required=True) #inbuilt validation by marshmallow
    views = marshmallow.fields.Integer(required=True)
    likes = marshmallow.fields.Integer(required=True)

    @validates('likes')
    def validate_likes(self, likes):
    	if likes > 1000:
    		raise ValidationError('The like Exceded the limit')
class VideoUpdateSchema(Schema):
    name = marshmallow.fields.String(validate=validate.Length(max=5), missing=None) #inbuilt validation by marshmallow
    views = marshmallow.fields.Integer(missing=None) #missing=None used for if the field missing value, it replaced as None
    likes = marshmallow.fields.Integer(missing=None)


class Video(Resource):
	@marshal_with(resource_fields)
	def get(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Could not find video with that ID")
		return result

	# @marshal_with(resource_fields)
	def put(self, video_id):
		# args = video_put_args.parse_args()

		try:
			args = request.get_json()
			schema = VideoSchema()
			video = schema.load(args)
			add_video = schema.dump(video)
			print(add_video)
		except ValidationError as err:
			print(err)
			print(err.valid_data)
			return err.messages, 422

		result = VideoModel.query.filter_by(id=video_id).first()
		if result:
			abort(409, message="Video id taken...")
		video = VideoModel(id=video_id, name=add_video['name'], views=add_video['views'], likes=add_video['likes'])
		db.session.add(video)
		db.session.commit()
		return jsonify({"message": "Video created!"})

	# @marshal_with(resource_fields)
	def patch(self, video_id): #or we can use 'put' here
		# args = video_update_args.parse_args()

		try:
			args = request.get_json()
			schema = VideoUpdateSchema()
			video = schema.load(args)
			add_video = schema.dump(video)
			print(add_video)
		except ValidationError as err:
			return err.messages, 422

		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot update.")

		if add_video['name']:
			result.name = add_video['name']
		if add_video['views']:
			result.views = add_video['views']
		if add_video['likes']:
			result.likes = add_video['likes']
		db.session.commit()
		
		return jsonify({"message": "Video Updated!"})


	def delete(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot deleted.")

		video = VideoModel.query.get(video_id)
		db.session.delete(video)
		db.session.commit()
		return jsonify({"message": "Video Deleted!"})

class VideoList(Resource):
	@marshal_with(resource_fields)
	def get(self):
		result = VideoModel.query.all()
		return result

class VideoSearchList(Resource):
	@marshal_with(random_fields)
	def get(self):
		data = request.args['data'] if request.args else None
		search_list = []
		if data:
			result = RandomLoader.query.filter(or_(
				RandomLoader.col1.contains(data),
				RandomLoader.col2.contains(data),
				RandomLoader.col3.contains(data),
				RandomLoader.col4.contains(data),
				RandomLoader.col5.contains(data),
				RandomLoader.col6.contains(data))).limit(20)
			for res in result:
				search_list.append(res)
		return search_list



api.add_resource(Video, "/videos/<int:video_id>")
api.add_resource(VideoList, "/videos")
api.add_resource(VideoSearchList, "/videos/search")


if __name__=="__main__":
	app.run(debug=True)