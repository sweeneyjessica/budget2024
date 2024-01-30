import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from budgetapp.db import get_db
from budgetapp.auth import login_required

bp = Blueprint('display', __name__, url_prefix='/display')

@bp.route('/debit')
@login_required
def debit():
    db = get_db()
    data = db.execute(
        'SELECT descr, amount'
        ' FROM debit d JOIN user u ON d.user_id = u.id'
        ' ORDER BY uploaded_at DESC'
    ).fetchmany(20)
    return render_template('display/display.html', headers=['Description', 'Amount'], data=data)


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


@bp.route('/categories')
@login_required
def categories():
    db = get_db()
    data = db.execute(
        'SELECT merchant, category, information, tags, uploaded_at'
        ' FROM merchant_to_category'
        ' ORDER BY uploaded_at DESC'
    ).fetchmany(20)
    return render_template('display/display.html', headers=['Merchant', 'Category', 'Information', 'Tags', 'Date Uploaded'], data=data)

@bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    data = db.execute(
        'SELECT m.category, round(sum(d.amount), 2)'
        ' FROM debit d JOIN merchant_to_category m ON d.descr = m.merchant'
        ' GROUP BY m.category'
    ).fetchall()
    return render_template('display/display.html', headers=['Category', 'Amount'], data=data)