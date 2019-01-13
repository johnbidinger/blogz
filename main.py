from flask import Flask, request, redirect, render_template, session, flash
from models import User, Blog
from app import db, app 
from validate import validate_, password_verify_same, empty_post
from hashutils import make_pw_hash, check_pw_hash

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    noerrors = True
    if request.method == 'POST':#submitted form
        #get form variables
        username = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #set error variables 
        _error = ""
        usererror = ""
        passerror = ""

        #validate username
        _error = validate_(username)
        if _error != "":
            noerrors = False
            usererror = "Username "+_error
            flash("Username <strong>{0}</strong> is not valid. {1}".format(username, usererror), 'danger')
            
        #validate password
        _error = password_verify_same(password, verify)
        if _error == "": #matching passwords
            _error = validate_(password) #check password meets required validation rules
            if  _error != "":
                noerrors = False
                passerror = "Password"+_error
                flash("{0}".format(passerror), 'danger')
                
        else:#non matching passwords
            noerrors = False
            passerror = "Password"+_error
            flash("{0}".format(passerror), 'danger')
        if noerrors:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:#not existing
                #add new user to db is all validation passed
                password = make_pw_hash(password)
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = username
                return redirect('/newpost')
                        
            else: #here if is existing user
                flash("The email <strong>{0}</strong> is already registered".format(username), 'danger')
            #return render_template('signup.html')
    #GET request
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = username
            flash("Logged in", 'info')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'danger')

    return render_template('login.html')
    

@app.route('/')
def index():
    users = User.query.all()
    blogs = Blog.query.all()
    return render_template('index.html', title="All Authors", users=users, blogs=blogs)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    if request.method == 'POST':
        return render_template('blog.html', title="My Blog Posts", 
                                blogs=blogs)
    
    if request.method == 'GET':
        if request.args.get('id'):
            id = request.args.get('id')
            blog = Blog.query.filter_by(id=id).first()
            return render_template('post.html', title="Blog Post", blog=blog)
        elif request.args.get('userID'):
            owner = request.args.get('userID')
            posts = Blog.query.filter_by(owner_id=owner).all()
            user = User.query.filter_by(id=owner).first()
            return render_template('singleUser.html', title="Posts by "+str(user.username), posts=posts)
        else:    
            return render_template('blog.html', title="My Blog Posts",
                            blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['email']).first()
        title_error="Title cannot be blank"
        body_error="Blog Body cannot be blank"
        #TODO owner_id property of Blog class

        if empty_post(blog_title) and empty_post(body):
            # if both title and body have content go here
            new_post = Blog(blog_title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            blog = Blog.query.filter_by(title=blog_title, body=body).first()
            return render_template('post.html', blog=blog)
        elif empty_post(blog_title): #returns true if title has content
            #if title is not empty body content error
            return render_template('newpost.html', blog_title=blog_title,
                                    body=body, body_error=body_error)
        elif empty_post(body):#returns true if body has content
            #if body is not empty title content error
            return render_template('newpost.html', blog_title=blog_title,
                                    body=body, title_error=title_error)
            
        else: #if both are empty body and title error
            return render_template('newpost.html', blog_title=blog_title,
                                    body=body, body_error=body_error, title_error=title_error)

    return render_template('newpost.html', title="New Post Page", blog_title="", body="")


if __name__ == '__main__':
    app.run()