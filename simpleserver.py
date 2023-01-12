from flask import Flask, jsonify, make_response, request, send_file
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import jwt
import datetime
from io import BytesIO
from zipfile import ZipFile
import ssl
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True)
 
app.config['SECRET_KEY']='1bb65c08cd5a8d41a28c822182890f15'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////root/app/bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
 
db = SQLAlchemy(app)


class Users(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   public_id = db.Column(db.Integer)
   name = db.Column(db.String(50))
   password = db.Column(db.String(50))
   admin = db.Column(db.Boolean)

#with app.app_context():
#    db.create_all()

#with app.app_context():
#    guest = Users(name='guest', password='7a28dfffa5e8178abc2240f05dd76cd4', admin=False, id=1, public_id=1)
#    db.session.add(guest)
#    db.session.commit()

# with app.app_context():
#    db.create_all()
#class Books(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#   user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#   name = db.Column(db.String(50), unique=True, nullable=False)
#   Author = db.Column(db.String(50), unique=True, nullable=False)
#   Publisher = db.Column(db.String(50), nullable=False)
#   book_prize = db.Column(db.Integer)


def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'Authorization' in request.headers:
           token = request.headers['Authorization']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           current_user = Users.query.filter_by(public_id=data['public_id']).first()
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator


@app.route('/')
@token_required
def hello_world():
    return "Hello World"

@app.route('/health')
def health():
    print("in health")
    return "Up and running"


@app.route('/login', methods=['POST']) 
def login_user():
   print("INSIDE LOGIN")
   auth = request.authorization  
   if not auth or not auth.username or not auth.password: 
       return make_response('could not verify', 401, {'Authentication': 'login required"'})   
 
   user = Users.query.filter_by(name=auth.username).first()  
   if user.password == auth.password:#check_password_hash(user.password, auth.password):
       token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
 
       return jsonify({'token' : token})
 
   return make_response('could not verify',  401, {'Authentication': '"login required"'})


#@app.route('/image/'


@app.route('/users', methods=['GET'])
def get_all_users():  
   users = Users.query.all()
   result = []  
   for user in users:  
       user_data = {}  
       user_data['public_id'] = user.public_id 
       user_data['name'] = user.name
       # user_data['password'] = user.password
       user_data['admin'] = user.admin
     
       result.append(user_data)  
   return jsonify({'users': result})


@app.route('/get_image', methods=['POST'])
@token_required
def get_image(*args, **kwargs):
  print("in get_image")
  print("args: %s" % args)
  print("kwargs: %s" % kwargs)
  print("data is: %s" % request.data)
  return send_file(request.data.decode().split("/")[-1])


@app.route('/get_images', methods=['POST'])
@token_required
def get_images(*args, **kwargs):
  print("in get_images")
  print("args: %s" % args)
  print("kwargs: %s" % kwargs)
  return ['https://137.184.187.8:8081/static/smiley.jpg', 'https://137.184.187.8:8081/static/smiley2.png']

#@app.route('/book', methods=['POST'])
#@token_required
#def create_book(current_user):
 
#   data = request.get_json()
#   new_books = Books(name=data['name'], Author=data['Author'], Publisher=data['Publisher'], book_prize=data['book_prize'], user_id=current_user.id) 
#   db.session.add(new_books)  
#   db.session.commit() 
#   return jsonify({'message' : 'new books created'})


#@app.route('/books', methods=['GET'])
#@token_required
#def get_books(current_user):
#   books = Books.query.filter_by(user_id=current_user.id).all()
#   output = []
#   for book in books:
#       book_data = {}
#       book_data['id'] = book.id
#       book_data['name'] = book.name
#       book_data['Author'] = book.Author
#       book_data['Publisher'] = book.Publisher
#       book_data['book_prize'] = book.book_prize
#       output.append(book_data)
 
#   return jsonify({'list_of_books' : output})


#@app.route('/books/<book_id>', methods=['DELETE'])
#@token_required
#def delete_book(current_user, book_id): 
 
#   book = Books.query.filter_by(id=book_id, user_id=current_user.id).first()  
#   if not book:  
#       return jsonify({'message': 'book does not exist'})  
 
#   db.session.delete(book) 
#   db.session.commit()  
#   return jsonify({'message': 'Book deleted'})
 
#if  __name__ == '__main__': 
#    app.run(debug=True)

# context = ssl.create_default_context()
# context.load_cert_chain("cert.pem", "key.pem")

#if __name__ == '__main__':
def run():
    print("starting")
    app.run(host="137.184.187.8", port=8081, ssl_context="adhoc", debug=True)
    print("running")
    #app.run(host="137.184.187.8", port=8081)
