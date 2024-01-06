from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQLの設定
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shimaT0915%'
app.config['MYSQL_DB'] = 'mybe'

mysql = MySQL(app)


from flask import render_template, request, redirect, url_for, flash, session, jsonify
import bcrypt

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['action'] == 'register':
            email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # データベースにユーザー情報を挿入
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            mysql.connection.commit()
            cur.close()

            flash('登録が成功しました！', 'success')
            return redirect(url_for('register'))  # 登録が成功したらログインページにリダイレクト

        elif request.form['action'] == 'login':
            email = request.form['email']
            password_candidate = request.form['password']

            # データベースからユーザーを取得
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and bcrypt.checkpw(password_candidate.encode('utf-8'), user['password'].encode('utf-8')):
                session['logged_in'] = True
                session['user_id'] = user['id']
                flash('ログインが成功しました！', 'success')
                return redirect(url_for('register'))
            else:
                flash('無効なログイン資格情報', 'danger')

    return render_template('test.html')

if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(debug=True)
