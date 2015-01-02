from auwebportal import app
from flask import render_template, request, make_response
from forms import InputForm
import datetime
from scrapper import Scrapper
import requests
import json


@app.route('/')
@app.route('/index')
@app.route('/index/')
def index():
    return render_template('index.html', title='AU Web Portal | A Python API Built Using Flask Microframework.')

@app.route('/test', methods=['GET', 'POST'])
@app.route('/test/', methods=['GET', 'POST'])
def fetch():
    form = InputForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('test.html', form=form)
        else:
            register_no = form.register_no.data
            dob = datetime.datetime.strptime(str(form.dob.data), '%Y-%m-%d').strftime('%d-%m-%Y')
            # # return "Form posted {0} {1}".format(register_no, dob)
            # # fetch_details(register_no, dob)
            # s = Scrapper(register_no, dob)
            # json_data = s.get_json()
            # return render_template('test.html', form=form, data=json_data)

            return render_template('test.html', form=form, valid=True)
    elif request.method == 'GET':
        return render_template('test.html', form=form)


def check_dob(dob):
    if dob == '':
        return False
    try:
        dob_split = dob.split('-')
        datetime.date(int(dob_split[2]), int(dob_split[1]), int(dob_split[0]))
        return True
    except:
        return False


def check_regno(register_no):
    if register_no != '' and register_no.isdigit() and len(register_no) > 8:
        return True
    else:
        False


@app.route('/get')
@app.route('/get/')
def get():
    register_no = request.args.get('register_no')
    dob = request.args.get('dob')

    if register_no is None or dob is None:
        resp = make_response(json.dumps({'error': 'Request parameters are not in correct format.'}))
    else:
        if not check_regno(register_no) and not check_dob(dob):
            resp = make_response(json.dumps({'error': 'Invalid Register Number and Date of Birth.'}))
        elif not check_regno(register_no):
            resp = make_response(json.dumps({'error': 'Invalid Register Number.'}))
        elif not check_dob(dob):
            resp = make_response(json.dumps({'error': "Date of Birth is invalid."}))
        else:
            s = Scrapper(register_no, dob)
            json_data = s.get_json()
            resp = make_response(json_data)

    resp.mimetype = 'application/json'
    return resp