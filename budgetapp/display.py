import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from budgetapp.db import get_db
from budgetapp.auth import login_required

import pandas as pd

bp = Blueprint('display', __name__, url_prefix='/display')

@bp.route('/debit', methods=('GET', 'POST'))
@login_required
def debit():
    db = get_db()
    data = db.execute(
        'SELECT descr, parsed_descr, amount'
        ' FROM debit d JOIN user u ON d.user_id = u.id'
        ' ORDER BY uploaded_at DESC'
    ).fetchall() #.fetchmany(20)
    return render_template('display/display.html', headers=['Description', 'Parsed Description', 'Amount'], data=data)


@bp.route('/credit')
@login_required
def credit():
    db = get_db()
    data = db.execute(
        'SELECT descr, amount'
        ' FROM credit c JOIN user u ON c.user_id = u.id'
        ' ORDER BY uploaded_at DESC'
    ).fetchmany(20)
    return render_template('display/display.html', headers=['Description', 'Amount'], data=data)


@bp.route('/capone')
@login_required
def capone():
    db = get_db()
    data = db.execute(
        'SELECT descr, -amount, uploaded_at'
        ' FROM credit c'
        ' UNION'
        ' SELECT descr, amount, uploaded_at'
        ' FROM debit d'
        ' ORDER BY uploaded_at DESC'
    ).fetchmany(20)
    return render_template('display/display.html', headers=['Description', 'Amount', 'Date Uploaded'], data=data)


@bp.route('/merchants')
@login_required
def categories():
    db = get_db()
    data = db.execute(
        'SELECT merchant, category, information, tags, uploaded_at'
        ' FROM merchants'
        ' ORDER BY uploaded_at DESC'
    ).fetchmany(20)
    return render_template('display/display.html', headers=['Merchant', 'Category', 'Information', 'Tags', 'Date Uploaded'], data=data)


@bp.route('/budget')
@login_required
def budget():
    db = get_db()
    data = db.execute(
        'SELECT category, dollar_limit, time_period'
        ' FROM budget'
    ).fetchall()
    return render_template('display/display.html', headers=['Category', 'Dollar Limit', 'Time Period'], data=data)

@bp.route('/scratch')
@login_required
def scratch():
    db = get_db()
    data = db.execute(
        'SELECT DISTINCT descr'
        'FROM debit'
    )

    df = pd.DataFrame(data)

    df['parsed']


@bp.route('/trash')
@login_required
def trash():
    # so technically you can't click any links to delete the user table, 
    # but you might be able to send a curl request that deletes stuff 
    # that the user shouldn't be able to see. need to look into db
    # permissions maybe? or maybe i can restrict this somehow with info
    # from the request object
    table = request.referrer.rsplit('/', maxsplit=1)[-1]
    db = get_db()
    db.execute(f'DELETE FROM {table}')
    db.commit()

    return redirect(url_for(f"display.{table}"))
