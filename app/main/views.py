from . import main
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response


@main.route('/')
def index():
    return render_template('index.html')
