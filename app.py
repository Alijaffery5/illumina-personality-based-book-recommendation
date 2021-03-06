from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt 
from flask_cors import CORS
import json
from datetime import datetime
import random
from collections import Counter

from mongoengine import connect
from mongoengine.queryset.visitor import Q
from mongoengine import DoesNotExist, NotUniqueError

from models import Shelves, Books, Users, Reviews

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.secret_key = 'secret'

CORS(app)

username = 'admin'
password = 'admin'
db = 'illumina'
host = f'mongodb+srv://{username}:{password}@illumina-lmf8b.gcp.mongodb.net/{db}?retryWrites=true&w=majority'

connect(host=host)

@app.route('/register', methods=["POST"])
@app.route('/book/register', methods=["POST"])
@app.route('/book-shelves/register', methods=['POST'])
def register():
    username = request.get_json()['username']
    email = request.get_json()['email']
    password = request.get_json()['password']
    date_of_birth = request.get_json()['dob']

    password = bcrypt.generate_password_hash(request.get_json()['password']).decode('utf-8')

    try:
        Users(
            username=username,
            email=email,
            date_of_birth=date_of_birth,
            password=password
        ).save()
    except NotUniqueError:
        return jsonify({"error":"Username or Email is not unique"})
    except:
        return jsonify({"error":"Registration Error, please try again"})

    return jsonify({'result' : email + ' registered'})

@app.route('/login', methods=['POST'])
@app.route('/book/login', methods=['POST'])
@app.route('/book-shelves/login', methods=['POSt'])
def login():
    login_id = request.get_json()['login_id']
    password = request.get_json()['password']

    try:
        response = Users.objects(Q(username=login_id) or Q(email=login_id)).get()
    except DoesNotExist as err:
        return jsonify({"user": "Invalid login id"})

    if bcrypt.check_password_hash(response['password'], password):
        session['user'] = response['username']

        return jsonify({'username': response['username'] , 'profile_pic': response['profile_pic']})
    else:
        return jsonify({"user":"Invalid Password"})

@app.route('/logout', methods=['POST'])
@app.route('/book/logout', methods=['POST'])
@app.route('/book-shelves/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"logout": True})

@app.route('/search', methods=['GET'])
def search_book():
    title = request.args.get('title', default = None, type = str)
    
    books = Books.objects(book_title__icontains=title).only(
        'book_title',
        'id',
        'cover_image',
        'avg_rating',
        'genres',
        'author'
    )

    lim = 10
    total = books.count()
    if total%lim != 0:
        total = int(total/lim) + 1
    else:
        total = int(total/lim)

    if 'user' in session:
        user = Users.objects(username=session['user']).get()
        shelves = []
        for shelf in user['shelves']:
            shelves.append(shelf['shelf_title'])

        return  jsonify({"books":books.to_json(), "total": total, "shelves": shelves})

    return  jsonify({"books":books.to_json(), "total": total})

@app.route('/book/<id>', methods=['GET'])
def get_book(id):
    try:
        book = Books.objects(id=id).get()
    except:
        return jsonify({"err": "Book not found"})
        
    if 'user' in session:
        user = Users.objects(username=session['user']).get()
        shelves = []
        for shelf in user['shelves']:
            shelves.append(shelf['shelf_title'])

        return  jsonify({"book":book.to_json(), "shelves": shelves})

    return  jsonify({"book":book.to_json()})
 
@app.route('/get-user', methods=['GET'])
@app.route('/book/get-user', methods=['GET'])
@app.route('/book-shelves/get-user', methods=['GET'])
def get_user():
    user = Users.objects(username=session['user']).get()
    return jsonify({"user":user.to_json()})

@app.route('/book/add-review', methods=['POST'])
def add_review():
    review = request.get_json()['review']
    book = request.get_json()['book']

    user = Users.objects(username=session['user']).only('username', 'profile_pic').get()
    book = Books.objects(id=book).get()

    try:
        book.reviews.get(username=session['user'])['review_text'] = review
    except DoesNotExist:
        book.reviews.append(Reviews(
            username=user['username'],
            profile_pic=user['profile_pic'],
            review_text=review
            ))

    book.save()
    
    return jsonify({"result": True})

@app.route('/book/rate-book', methods=['POST'])
def rate_book():
    book_id = request.get_json()['book']
    rating = request.get_json()['rating']
 
    book = Books.objects(id=book_id).get()

    try:
        book.reviews.get(username=session['user'])['rating'] = rating
        book.reviews.get(username=session['user'])['created'] = datetime.utcnow()
    except DoesNotExist:
        user = Users.objects(username=session['user']).only('username', 'profile_pic').get()
        book.reviews.append(Reviews(
            username=user['username'],
            profile_pic=user['profile_pic']
        ))

    book.save()

    return jsonify({"result": True})

@app.route('/book-shelves/add-shelf', methods=['POST'])
@app.route('/add-shelf', methods=['POST'])
def add_shelf():
    shelf = request.get_json()['shelf']
    user = Users.objects(username=session['user']).get()
    user.shelves.append(Shelves(
        shelf_title=shelf
    ))
    user.save()
    return jsonify({"result": True})

@app.route('/add-book-to-shelf', methods=['POST'])
@app.route('/book/add-book-to-shelf', methods=['POST'])
def add_book_to_shelf():
    shelf = request.get_json()['shelf']
    book = request.get_json()['book']

    user = Users.objects(username=session['user']).get()

    user.shelves.get(shelf_title=shelf).shelved_books.append(
        Books.objects(id=book).get()
    )
    user.save()
    return jsonify({"result": True})

@app.route('/get-user-shelf', methods=['GET'])
@app.route('/book-shelves/get-user-shelf', methods=['GET'])
def get_user_shelf():
    user = Users.objects(username=session['user']).get()

    shelves = []
    for shelf in user.shelves:
        books = []
        for book in shelf.shelved_books:
            books.append(
                {
                'id': str(book.id),
                'title': book.book_title,
                'cover_image': book.cover_image,
                'author': book.author
                }
            )
        shelves.append(
            {
            "shelf_title": shelf.shelf_title,
            "shelf_pic": shelf.shelf_pic,
            "books": books
            }
        )

    return jsonify({"shelves": json.dumps(shelves)})

@app.route('/get-book-recommendation', methods=['GET'])
def get_book_recommendation():
    user = Users.objects(username=session['user']).get()

    genres = []
    ignore_books = []
    for shelf in user.shelves:
        for book in shelf.shelved_books:
            ignore_books.append(book['id'])
            for genre in book.genres:
                genres.append(genre)

    genres = list(dict(Counter(genres).most_common()).keys())

    if len(genres) > 5:
        genres = genres[:5]

    books = Books.objects(
        Q(avg_rating__gte=4.5) & Q(genres__in=list(genres)) & Q(id__nin=list(set(ignore_books)))
        ).only(
        'book_title',
        'id',
        'cover_image',
        'author',
        'genres',
        'avg_rating'
    ).to_json()
    
    books = json.loads(books)
    books = random.sample(books,6)

    return jsonify({"rec": json.dumps(books)})

@app.route('/book/remove-review', methods=['POST'])
def remove_review():
    book = request.get_json()['book']

    book = Books.objects(id=book).get()
    book.reviews.remove(book.reviews.get(username=session['user']))
    book.save()

    return jsonify({'result': True})

@app.route('/remove-shelf-book', methods=['POST'])
def remove_shelf_book():
    book = request.get_json()['book']
    shelf = request.get_json()['shelf']

    user = Users.objects(username=session['user']).get()
    user.shelves.get(shelf_title=shelf).shelved_books.remove(Books.objects(id=book).get())
    
    user.save()

    return jsonify({'result': True})

@app.route('/remove-shelf', methods=['POST'])
def remove_shelf():
    shelf = request.get_json()['shelf']

    user = Users.objects(username=session['user']).get()
    user.shelves.remove(user.shelves.get(shelf_title=shelf))
    
    user.save()

    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)

# add user, genre, author to search | not doing
# add remove button to book shelves for shelf and books | done
# create profile form
# create personality graph