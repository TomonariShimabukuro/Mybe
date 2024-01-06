from flask import Flask, render_template, request, redirect, url_for, flash
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

    return redirect(url_for('index'))

# mypage.htmlへのルート
@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
