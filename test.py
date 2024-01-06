from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQLの設定
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shimaT0915%'
app.config['MYSQL_DB'] = 'mybe'

mysql = MySQL(app)


# Flaskアプリケーションのコード
from flask import Flask, render_template, request, redirect, url_for, flash, session
import bcrypt

app = Flask(__name__)

# セッションのセキュリティキー
app.secret_key = 'your_secret_key'

# ルート - ログインと登録
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            # ログイン処理
            email = request.form['email']
            password = request.form['password']
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['logged_in'] = True
                session['user_id'] = user['id']
                flash('ログインが成功しました！', 'success')
                return redirect(url_for('register'))
            else:
                flash('無効なログイン資格情報', 'danger')

        elif action == 'register':
            # 登録処理
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password == confirm_password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                # データベースにユーザー情報を挿入
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
                mysql.connection.commit()
                cur.close()

                flash('登録が成功しました！', 'success')
            else:
                flash('パスワードが一致しません', 'danger')

    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(debug=True)
