from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz2:blogz2@localhost:8889/blogz2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'xy337KGys&'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title,content,owner):
        self.title = title
        self.content = content
        self.owner = owner
       
class User(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref ='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    if request.method == 'POST':
        task_name = request.form['task']
        new_blog = request.form['new_blog']
        if (len(task_name) == 0):
            return render_template('newpost.html', title_error="title can't be empty")
        if (len(new_blog) == 0):
            return render_template('newpost.html', content_error="content can't be empty")
        owner = User.query.filter_by(username=session['username']).first()
        new_task = Blog(task_name, new_blog, owner)
        db.session.add(new_task)
        db.session.commit()
        return redirect('/blog/' + str(new_task.id))
    if request.method == 'GET':
        form_value = request.args.get('user')
        if (form_value):
            task = db.session.query(Blog).filter_by(owner_id=form_value).all()
        else:
            task = db.session.query(Blog).all()
        return render_template('todos.html',
            tasks=task)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route('/blog/<int:id>', methods=['GET'])
def blog(id):
    post = db.session.query(Blog).filter_by(id=id).scalar()
    return render_template('blog.html',post=post)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if (request.method == 'GET'):
        return render_template('signup.html')
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']
        if (len(username) < 3):
            return render_template('signup.html', name_error="user field is empty or too short", user_name=username)
        if (len(password) < 3):
            return render_template('signup.html', pwd_error="password field is empty or too short", user_name=username)
        if (len(verifypassword) == 0):
            return render_template('signup.html', vpwd_error="verify password field is blank", user_name=username)
        if (password != verifypassword):
            return render_template('signup.html', vpwd_error="passwords don't match", user_name=username)
        exisiting_user = User.query.filter_by(username = username).first()
        if not exisiting_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', name_error="user already exists", user_name=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'GET'):
        return render_template('login.html')
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        userobject = User.query.filter_by(username = username).first()
        if userobject:
            if userobject.password == password:
                session['username'] = username
                return redirect('/newpost') 
            else:
                return render_template('login.html', pwd_error="wrong password", usernamevalue= username)
        else:
            return render_template('login.html', uname_error="user doesn't exist", usernamevalue= username)

@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html')

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()