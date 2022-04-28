from flask_app import app
from flask import render_template, request, redirect, session, flash
from flask_app.models.painting import Painting
from flask_app.models.user import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": session['user_id']
    }
    return render_template('dashboard.html', user = User.get_by_id(data), all_paintings = Painting.get_all_paintings_with_users())

@app.route('/paintings/new')
def new_painting():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": session['user_id']
    }
    user = User.get_by_id(data)
    return render_template('create.html', user = user)

@app.route('/paintings/<int:id>/edit')
def edit_painting(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id":id
    }
    painting = Painting.get_one_painting_with_user(data)
    return render_template('edit.html', painting = painting)

@app.route('/paintings/<int:id>')
def read_painting(id):
    if 'user_id' not in session:
        return redirect('/logout')
    painting_data = {
        "id": id
    }
    return render_template('read.html', this_painting = Painting.get_one_painting_with_user(painting_data))

@app.route('/delete/<int:id>')
def delete_painting(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id":id
    }
    Painting.delete(data)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# POST METHODS

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': pw_hash
    }
    user_id = User.save(data)
    session['user_id'] = user_id
    return redirect('/dashboard')

@app.route('/login', methods = ['POST'])
def login():
    data = {
        "email": request.form['email']
    }
    user_in_db = User.get_by_email(data)
    if not user_in_db:
        flash('Invalid Email/Password', 'login')
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash('Invalid Email/Password', 'login')
        return redirect('/')
    session['user_id'] = user_in_db.id
    return redirect('/dashboard')

@app.route('/create', methods=['POST'])
def create_painting():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Painting.validate_painting(request.form):
        return redirect('/paintings/new')
    data = {
        "title": request.form['title'],
        "description": request.form['description'],
        "price": int(request.form['price']),
        "user_id": session["user_id"]
    }
    Painting.save(data)
    return redirect('/dashboard')

@app.route('/update/<int:id>', methods = ['POST'])
def update_painting(id):
    if 'user_id' not in session:
        return redirect('/logout')
    if not Painting.validate_painting(request.form):
        return redirect(f'/paintings/{id}/edit')
    data = {
        "id": id,
        "title": request.form["title"],
        "description": request.form["description"],
        "price": request.form["price"]
    }
    Painting.update(data)
    return redirect('/dashboard')

