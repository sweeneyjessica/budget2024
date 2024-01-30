import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.utils import secure_filename

from budgetapp.db import get_db
from budgetapp.auth import login_required
import csv
import os

bp = Blueprint('upload', __name__)

@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filetype = request.form['filetype']
        db = get_db()
        error = None

        if not file:
            error = 'File is required.'
        if not filetype:
            error = 'File type must be specified.'

        if error is None:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            with open(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                firstRow = True

                for row in reader:
                    if firstRow:
                        firstRow = False
                        continue

                    if len(row) < 7: 
                        continue # change to quarantine at some point

                    if row[5] != '': # debit 
                        db.execute(
                            "INSERT INTO debit (user_id, transaction_date, card_no, descr, amount) VALUES (?, ?, ?, ?, ?)",
                            (g.user['id'], row[0], row[2], row[3], row[5])
                        )
                        db.commit()
                    elif row[6] != '': #credit
                        db.execute(
                            "INSERT INTO credit (user_id, transaction_date, card_no, descr, amount) VALUES (?, ?, ?, ?, ?)",
                            (g.user['id'], row[0], row[2], row[3], row[6])
                        )
                        db.commit()
                    else:
                        db.execute(
                            "INSERT INTO transaction_quarantine (user_id, transaction_date, card_no, descr) VALUES (?, ?, ?, ?)",
                            (g.user['id'], row[0], row[2], row[3])
                        )
                        db.commit()
                        error = "No transaction amount found."

            return redirect(url_for('display.display'))
        
        flash(error)

    return render_template('upload/upload.html')

