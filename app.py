from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:shimaT0915%@shori.local/mybe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Set your own secret key

# Creating SQLAlchemy and Flask-Admin objects without app context
db = SQLAlchemy(app)
admin = Admin(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    data = db.Column(db.LargeBinary)
    description = db.Column(db.String(255))



# Creating the admin view within the app context
with app.app_context():
    db.create_all()
    admin.add_view(ModelView(Image, db.session))

@app.route('/')
def index():
    # Displaying the list of images
    images = Image.query.all()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        filename = file.filename
        data = file.read()
        description = request.form['description']

        new_image = Image(filename=filename, data=data, description=description)
        db.session.add(new_image)
        db.session.commit()

        return redirect(url_for('index'))

    except KeyError:
        return "No 'file' key found in request", 400

if __name__ == '__main__':
    app.run(debug=True)

