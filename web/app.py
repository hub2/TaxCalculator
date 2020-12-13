import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import secrets

from stock_market_tax import calculate_tax, load_user_transactions_from_file

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secrets.token_hex(64)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=["POST", "GET"])
def tax():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secrets.token_hex(16) + "_" + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('tax_calculations',
                                    filename=filename))
    return render_template("upload.html")

@app.route('/uploads/<filename>')
def tax_calculations(filename):
    columns, transactions = load_user_transactions_from_file(os.path.join(app.config["UPLOAD_FOLDER"],filename))
    sv = calculate_tax(transactions)

    return render_template("calculations.html", sv=sv)


if __name__ == '__main__':
    app.run()
