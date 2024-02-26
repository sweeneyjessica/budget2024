import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.utils import secure_filename

from budgetapp.db import get_db
from budgetapp.auth import login_required
from budgetapp.parsing import parse_value, auto_label

import csv
import os
import pandas as pd 

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

                    if filetype == 'capone':
                        if len(row) != 7: 
                            continue # change to quarantine at some point
                        
                        parsed_descr = parse_value(row[3])

                        if row[5] != '': # debit 
                            db.execute(
                                "INSERT INTO debit (user_id, transaction_date, card_no, descr, parsed_descr, amount) VALUES (?, ?, ?, ?, ?, ?)",
                                (g.user['id'], row[0], row[2], row[3], parsed_descr, row[5])
                            )
                            db.commit()
                        elif row[6] != '': #credit
                            db.execute(
                                "INSERT INTO credit (user_id, transaction_date, card_no, descr, parsed_descr, amount) VALUES (?, ?, ?, ?, ?, ?)",
                                (g.user['id'], row[0], row[2], row[3], parsed_descr, row[6])
                            )
                            db.commit()
                        else:
                            db.execute(
                                "INSERT INTO transaction_quarantine (user_id, transaction_date, card_no, descr, parsed_descr) VALUES (?, ?, ?, ?, ?)",
                                (g.user['id'], row[0], row[2], row[3], parsed_descr)
                            )
                            db.commit()
                            error = "No transaction amount found."

                    elif filetype == 'categories':
                        if len(row) != 4:
                            continue
                        try:
                            db.execute(
                                'INSERT INTO merchants (merchant, category, information, tags) VALUES (?, ?, ?, ?)',
                                (parse_value(row[0]), row[1], row[2], row[3])
                            )
                            db.commit()
                        except:
                            db.execute(
                                'INSERT INTO merchants_quarantine (merchant, category, information, tags) VALUES (?, ?, ?, ?)',
                                (parse_value(row[0]), row[1], row[2], row[3])
                            )
                            db.commit()


            return redirect(url_for(f'display.{filetype}'))
        
        flash(error)

    return render_template('upload/upload.html')

@bp.route('/set-budget', methods=('GET', 'POST'))
@login_required
def set_budget():
    db = get_db()

    if request.method == 'POST':
        for category in request.form:
            db.execute(
                'REPLACE INTO budget (category, dollar_limit) VALUES (?, ?)',
                (category, request.form[category])
            )
            db.commit()
        return redirect(url_for('display.budget'))
    else:
        categories = db.execute(
            'SELECT DISTINCT category '
            ' FROM merchants'
        ).fetchall()

    return render_template('upload/set_budget.html', categories=categories)

@bp.route('/categorize-merchants', methods=('GET', 'POST'))
@login_required
def categorize_merchant():
    db = get_db()

    # txns = db.execute(
    #     'SELECT descr, amount, transaction_date'
    #     ' FROM debit'
    #     ' WHERE amount > 20.0'
    #     ' GROUP BY descr'
    #     # ' WHERE COUNT(descr) > 1 AND amount > 20.0'
    # ).fetchall()

    # list of all descriptions where:
    #  - there are 2+ of that description in dataset
    #  - the average amount is > $20

    txns = db.execute(
        'SELECT parsed_descr, COUNT(*) AS num_txns, AVG(amount) AS average_amount'
        ' FROM debit'
        ' GROUP BY parsed_descr'
    ).fetchall()

    df = pd.DataFrame(txns)
    df.columns = ['parsed_descr', 'num_txns', 'average_amount']

    labeled_df, unlabeled_df = auto_label(df)
    unlabeled_descr = unlabeled_df['parsed_descr']
    unlabeled_count = unlabeled_df['num_txns']
    unlabeled_amount = unlabeled_df['average_amount']

    unlabeled_df = [[descr, count, amount] for descr, count, amount in zip(unlabeled_descr, unlabeled_count, unlabeled_amount)]

    for index, row in labeled_df.iterrows():
        db.execute('INSERT OR REPLACE INTO merchants (merchant, category, information, tags) VALUES (?, ?, ?, ?)',
                (row['parsed_descr'], row['Category'], row['Information'], row['Tags'])
        )
        db.commit()

    fields = ['Category', 'Information', 'Tags']

    if request.method == 'POST':
        for_each_merchant = {key: "" for key in fields}
        for merchant_field in request.form:
            merchant = merchant_field.rsplit(":", maxsplit=1)[0]
            field = merchant_field.rsplit(":", maxsplit=1)[1]

            for_each_merchant[field] = request.form[merchant_field]

            if field == fields[-1]:
                db.execute(
                    'REPLACE INTO merchants (merchant, category, information, tags) VALUES (?, ?, ?, ?)',
                    (merchant, for_each_merchant['Category'], for_each_merchant['Information'], for_each_merchant['Tags'])
                )
                db.commit()
                for_each_merchant = {key: "" for key in fields}

        data = db.execute('SELECT * FROM merchants')
        return render_template('display/display.html', headers=['Merchant', 'Category', 'Information', 'Tags', 'Uploaded At'], data=data)

    return render_template('upload/categorize_merchants.html', headers=['Description', 'Count', 'Average']+fields, data=unlabeled_df, fields=fields)
