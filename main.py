from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hello@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    if request.method == 'GET':
        return render_template("new-post.html")
    elif request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if_error = False

        if blog_title == '':
            flash('Please fill in the title', category='title_error')
            if_error = True
        if blog_body == '':
            flash('Please fill in the blog entry', category='body_error')
            if_error = True
        if if_error:
            return render_template("new-post.html")

        new_post = Blog(blog_title, blog_body)
        db.session.add(new_post)
        db.session.commit()
        id = str(new_post.id)

        return redirect('/?id=' + id)

@app.route('/', methods=['POST', 'GET'])
def index():
    encoded_id = request.args.get("id")
    blogs = Blog.query.filter_by(id=Blog.id).all()
    title = Blog.query.filter_by(title=Blog.title).first()

    if request.method == 'POST':
        return render_template('blog.html', title=title, id=encoded_id, blogs=blogs)

    if request.method == 'GET':
        blog = Blog.query.filter_by(id=encoded_id).first()
        return render_template('blog.html', title="Build a Blog", encoded_id=encoded_id, blog=blog, blogs=blogs)


if __name__ == '__main__':
    app.run()
