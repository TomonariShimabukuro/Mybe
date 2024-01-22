from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import bcrypt
from flask_mysqldb import MySQL
import os
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MySQLの接続情報を設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:shimaT0915%@localhost/mybe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shimaT0915%'
app.config['MYSQL_DB'] = 'mybe'
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
mysql = MySQL(app)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['action'] == 'register':
            email = request.form['email']
            password = request.form['password']

            # 入力検証
            if not email or not password:
                flash('メールアドレスとパスワードを入力してください。', 'danger')
                return redirect(url_for('register'))

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # データベースにユーザー情報を挿入
            with mysql.connection.cursor() as cur:
                cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
                mysql.connection.commit()

            flash('登録が成功しました！ログインしてください。', 'success')
            return redirect(url_for('register'))  # 登録が成功したらログインページにリダイレクト

        elif request.form['action'] == 'login':
            email = request.form['email']
            password_candidate = request.form['password']

            # データベースからユーザーを取得
            with mysql.connection.cursor() as cur:
                cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
                user = cur.fetchone()

            if user and bcrypt.checkpw(password_candidate.encode('utf-8'), user['password'].encode('utf-8')):
                session['logged_in'] = True
                session['user_id'] = user['id']
                flash('ログインが成功しました！', 'success')
                return render_template('mypage.html')
            else:
                flash('無効なログイン資格情報', 'danger')

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        # データベースからユーザーを取得
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

        if user and bcrypt.checkpw(password_candidate.encode('utf-8'), user[1].encode('utf-8')):
            session['logged_in'] = True
            session['user_id'] = user[0]
            with mysql.connection.cursor() as cur:
                cur.execute("SELECT id FROM images WHERE user_id = %s", (user[0],))
                images = cur.fetchall()
            return render_template('mypage.html', images=images)
        else:
            flash('メールアドレスもしくはパスワードが正しくありません', 'danger')
            return render_template('index.html')


    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'logged_in' not in session:
        flash('ログインしていません', 'danger')
        return redirect(url_for('login'))
    # ログインしている場合、ユーザーIDと画像ファイル名を取得
    if 'user_id' in session:
        user_id = session['user_id']


    

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # 固有のファイル名を生成
                unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)

                # アップロードされた画像を保存
                user_id = session['user_id']  # ログインしているユーザーのIDを取得
                user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))

                if not os.path.exists(user_folder):
                    os.makedirs(user_folder)

                filename = os.path.join(user_folder, unique_filename)
                file.save(filename)

                # タグ情報を取得
                tag = request.form.get('tag', '')

                # タグが指定された4つの値のいずれかであるか確認
                if tag not in ['mybe-log', 'salon-log', 'favorite', 'like']:
                    flash('無効なタグ', 'danger')
                    return redirect(url_for('upload'))

                # データベースにファイル名とタグ、ユーザーIDを保存
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO images (filename, tag, user_id) VALUES (%s, %s, %s)",
                            (unique_filename, tag, user_id))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('upload'))

    # ユーザーごとの画像のリストを取得
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM images WHERE user_id = %s", (user_id,))

    # タプルのリストからディクショナリのリストに変換
    images = [{'filename': row[1], 'tag': row[2]} for row in cur.fetchall()]

    cur.close()

    return render_template('upload.html', images=images)



# 画像を削除するためのルート
@app.route('/delete/<filename>', methods=['GET'])
def delete(filename):
    
    # ファイルを削除
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)

        # データベースからも削除
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM images WHERE filename = %s", (filename,))
        mysql.connection.commit()
        cur.close()
        flash(f'File {filename} deleted successfully', 'success')
    else:
        flash(f'File {filename} not found', 'danger')

    return redirect(url_for('upload'))

@app.route('/tag/<tag>')
def tag_page(tag):
    # Imageモデルからtagに一致する画像を取得するクエリ
    images_with_tag = images.query.filter_by(tag=tag).all()

    # 取得した画像をHTMLテンプレートに渡して表示
    return render_template('tag_page.html', images=images_with_tag, tag=tag)



# /mypageにアクセスするためのルート
@app.route('/mypage')
def mypage():
    # ログインするとmypageにアクセス可能に
    if 'logged_in' not in session:
        flash('ログインしていません', 'danger')
        return redirect(url_for('login'))
    # 各タグごとの画像をデータベースから取得
    salon_log_images = get_tag_images('salon-log')
    mybe_log_images = get_tag_images('mybe-log')
    favorite_images = get_tag_images('favorite')
    like_images = get_tag_images('like')

    return render_template('mypage.html',
                           salon_log_images=salon_log_images,
                           mybe_log_images=mybe_log_images,
                           favorite_images=favorite_images,
                           like_images=like_images)

def get_tag_images(tag):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM images WHERE tag = %s", (tag,))
    images = [{'filename': row[1]} for row in cur.fetchall()]
    cur.close()
    return images
    

# Flask-Adminの初期化
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

class images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    data = db.Column(db.LargeBinary)
    description = db.Column(db.String(255))
    tag = db.Column(db.String(255))

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))

# usersモデルとimagesモデルをFlask-Adminに登録
admin.add_view(ModelView(users, db.session))
admin.add_view(ModelView(images, db.session))


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(debug=True)