import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from wtforms import SubmitField, TextAreaField, StringField, PasswordField
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import render_template
from flask import redirect


app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)

migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    generated_content = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')

class UserInfoForm(FlaskForm):
    text = TextAreaField('Enter your text')
    image = FileField('Upload an image', validators=[FileAllowed(['jpg', 'jpeg'], 'Only JPEG images allowed')])
    submit = SubmitField('Submit')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful')

            # Redirect to the specified homepage after successful login
            return redirect(url_for('specified_homepage'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)



@app.route('/specified_homepage')
def specified_homepage():
    # Retrieve all user-generated content from the database
    all_users_content = User.query.with_entities(User.id, User.generated_content).all()
    return render_template('specified_homepage.html', all_users_content=all_users_content)




@app.route('/user_page', methods=['GET', 'POST'])
@login_required
def user_page():
    form = UserInfoForm()
    if form.validate_on_submit():
        text = form.text.data
        image = form.image.data

        if text or image:
            current_user.generated_content = f'Text: {text}' if text else ''
            if image:
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                current_user.generated_content += f'<img src="{{ url_for("static", filename="uploads/{image_filename}") }}" alt="Uploaded Image">'
            db.session.commit()
            flash('Content submitted successfully')
            
            # Redirect to the specified homepage after submitting content
            return redirect(url_for('specified_homepage'))
        else:
            flash('Please submit at least text or an image')

    return render_template('user_page.html', form=form, user_content=current_user.generated_content)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("Signup route is called.")
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password != confirm_password:
            flash('Passwords do not match. Please try again.')
        elif User.query.filter_by(id=username).first():
            flash('Username is already taken. Please choose another.')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(id=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please log in.')
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, threaded=False)



