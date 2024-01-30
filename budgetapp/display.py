import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from budgetapp.db import get_db
from budgetapp.auth import login_required

bp = Blueprint('display', __name__)

@bp.route('/display')
@login_required
def display():
    db = get_db()
    data = db.execute(
        'SELECT descr, amount'
        ' FROM debit d JOIN user u ON d.user_id = u.id'
        ' ORDER BY uploaded_at DESC'
    ).fetchmany(20)
    return render_template('display/display.html', data=data)