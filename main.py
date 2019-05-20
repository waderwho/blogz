from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hello@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def logged_in_user():
    return User.query.filter_by(username=session['username']).first()

def get_user_blogs(user_id):
    return Blog.query.filter_by(owner_id=user_id).all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Welcome back ' + username)
            return redirect('/new-post')
        else:
            flash('User Password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and password == verify and username != '':
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new-post')
        else:
            return "<h1>Username is already in use.</h1>"

    return render_template('signup.html')

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    if request.method == 'GET':
        return render_template("new-post.html")
    elif request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_owner = User.query.filter_by(username=session['username']).first()
        if_error = False

        if blog_title == '':
            flash('Please fill in the title')
            if_error = True
        if blog_body == '':
            flash('Please fill in the blog entry')
            if_error = True
        if if_error:
            return render_template("new-post.html")

        new_post = Blog(blog_title, blog_body, blog_owner)
        db.session.add(new_post)
        db.session.commit()
        id = str(new_post.id)

        return redirect("/?id=" + id)

@app.route('/blog')
def blog():
    encoded_id = request.args.get("id")
    encoded_user = request.args.get("user")
    all_blogs = Blog.query.all()
    blog = Blog.query.filter_by(id=encoded_id).first()

    if encoded_user == '':
        flash('You must login to view your blog')
        return redirect('/blog')

    if encoded_user:
        user = User.query.filter_by(username=encoded_user).first()
        user_blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('singleUser.html', all_blogs=all_blogs, user_blogs=user_blogs, blog=blog, encoded_user=encoded_user)

    return render_template('singleUser.html', all_blogs=all_blogs, blog=blog, encoded_id=encoded_id)


@app.route('/')
def index():
    return render_template('index.html', users=User.query.all())


if __name__ == '__main__':
    app.run()
