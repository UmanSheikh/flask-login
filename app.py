# Importing the libraries
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

# App Configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'veryimportantsecret'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))

class Routes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route1 = db.Column(db.String(80))
    route2 = db.Column(db.String(80))

class Assignments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(80))
    driver = db.Column(db.String(80))
    vnumber = db.Column(db.String(80))
    vname = db.Column(db.String(80))

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(80))
    status = db.Column(db.String(80))

# Routes
@app.route('/')
@login_required
def index():
    routes = Routes.query.all()
    return render_template('index.html', routes=routes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if user.password == request.form['password']:
                login_user(user)
                return redirect(url_for('index'))
        return '<h1>Invalid username or password</h1>'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(email=request.form['email'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        route = Routes(route1=request.form['routeA'], route2=request.form['routeB'])
        db.session.add(route)
        db.session.commit()
        return redirect(url_for('routes'))
    return render_template('add_routes.html')

@app.route('/routes')
@login_required
def routes():
    routes = Routes.query.all()
    return render_template('routes.html', routes=routes)

@app.route('/deleteRoute/<int:id>')
@login_required
def deleteRoute(id):
    route = Routes.query.get_or_404(id)
    try:
        db.session.delete(route)
        db.session.commit()
        return redirect('/routes')
    except:
        return 'There was a problem deleting that route'


@app.route('/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign(id):
    if request.method == 'POST':
        assignment = Assignments(route=str(Routes.query.get_or_404(id).route1 + '-' + Routes.query.get_or_404(id).route2), driver=request.form['driver'], vnumber=request.form['vnumber'], vname=request.form['vname'])
        db.session.add(assignment)
        db.session.commit()
        return redirect(url_for('assignments'))
    route = Routes.query.get_or_404(id)
    return render_template('assign.html', route=route)

@app.route('/assignments')
@login_required
def assignments():
    assignments = Assignments.query.all()
    return render_template('assignments.html', assignments=assignments)

@app.route('/deleteAssignment/<int:id>')
@login_required
def deleteAssignment(id):
    assignment = Assignments.query.get_or_404(id)
    try:
        db.session.delete(assignment)
        db.session.commit()
        return redirect('/assignments')
    except:
        return 'There was a problem deleting that assignment'

@app.route('/track/<int:id>', methods=['GET', 'POST'])
@login_required
def track(id):
    if request.method == 'POST':
        track = Track(route=str(Routes.query.get_or_404(id).route1 + '-' + Routes.query.get_or_404(id).route2), status=request.form['status'])
        db.session.add(track)
        db.session.commit()
        return redirect(url_for('track_view'))
    route = Routes.query.get_or_404(id)
    return render_template('track.html', route=route )

@app.route('/track')
@login_required
def track_val():
    routes = Routes.query.all()
    return render_template('track_val.html', routes=routes)

@app.route('/track_view')
@login_required
def track_view():
    tracks = Track.query.all()
    return render_template('track_view.html', tracks=tracks)

@app.route('/deleteTrack/<int:id>')
@login_required
def deleteTrack(id):
    track = Track.query.get_or_404(id)
    try:
        db.session.delete(track)
        db.session.commit()
        return redirect('/track_view')
    except:
        return 'There was a problem deleting that track'

# Main route
if __name__ == '__main__':
    if not os.path.exists('database.db'):
        app.app_context().push()
        db.create_all()
    app.run(debug=True)