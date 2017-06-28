from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(120))

    def __init__(self, title,content):
        self.title = title
        self.content = content
       


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_blog = request.form['new_blog']
        new_task = Task(task_name, new_blog)
        db.session.add(new_task)
        db.session.commit()

    task = Task.query.all()
    return render_template('todos.html',title="Get It Done!", 
        tasks=task)

@app.route('/new')
def new():
    return render_template('new.html')

@app.route('/blog/<int:id>', methods=['GET'])
def blog(id):
    post = db.session.query(Task).filter_by(id=id).scalar()
    return render_template('blog.html',post=post)

if __name__ == '__main__':
    app.run()