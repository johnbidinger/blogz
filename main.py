from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
#from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner   

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password




@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    if request.method == 'POST':
        return render_template('blog.html', title="My Blog Posts", 
                                blogs=blogs)
    
    if request.method == 'GET':
        if not request.args.get('id'):
            return render_template('blog.html', title="My Blog Posts",
                            blogs=blogs)
        else:
            id = request.args.get('id')
            blog = Blog.query.filter_by(id=id).first()
            return render_template('post.html', title="Blog Post", blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']
        #TODO owner_id property of Blog class
        if empty_post(blog_title) and empty_post(body):
            # if both title and body have content go here
            new_post = Blog(blog_title, body)
            db.session.add(new_post)
            db.session.commit()
            blog = Blog.query.filter_by(title=blog_title, body=body).first()
            return render_template('post.html', blog=blog)
        elif empty_post(blog_title): #returns true if title has content
            #if title is not empty body content error
            body_error="Blog Body cannot be blank"
            return render_template('newpost.html', blog_title=blog_title,
                                    body=body, body_error=body_error)
        elif empty_post(body):#returns true if body has content
            #if body is not empty title content error
            title_error="Title cannot be blank"
            return render_template('newpost.html', blog_title=blog_title,
                                    body=body, title_error=title_error)
            
        else: #if both are empty body and title error
            title_error="Title cannot be blank"
            body_error="Blog Body cannot be blank"
            return render_template('newpost.html', blog_title=blog_title,
                                    body=body, body_error=body_error, title_error=title_error)

    return render_template('newpost.html', title="New Post Page", blog_title="", body="")

def empty_post(content):
    if not content:
        return False
    return True
if __name__ == '__main__':
    app.run()