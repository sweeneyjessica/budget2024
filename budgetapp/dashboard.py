import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from budgetapp.db import get_db
from budgetapp.auth import login_required
import matplotlib.pyplot as plt


bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    data = db.execute(
        'SELECT category, sum(amount)'
        ' FROM debit d JOIN merchant_to_category m ON d.descr = m.merchant'
        ' GROUP BY category'
    )