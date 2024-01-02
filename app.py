from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# MySQLの接続情報を設定
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shimaT0915%'
app.config['MYSQL_DB'] = 'image_gallery'
app.config['UPLOAD_FOLDER'] = 'static/images'

mysql = MySQL(app)

# 画像をアップロードするためのルート
@app.route('/')
def index():
    # データベースから画像のリストを取得
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM images")
    
    # タプルのリストからディクショナリのリストに変換
    images = [{'filename': row[1]} for row in cur.fetchall()]
    
    cur.close()

    return render_template('upload.html', images=images)

# 画像をアップロードするためのルート
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            # アップロードされた画像を保存
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # データベースにファイル名を保存
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO images (filename) VALUES (%s)", (file.filename,))
            mysql.connection.commit()
            cur.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
