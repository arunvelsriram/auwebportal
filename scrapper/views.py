from . import app
from flask import render_template, flash, request
from forms import InputForm
import datetime
from .scrapper import Scrapper


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test', methods=['GET', 'POST'])
def fetch():
    form = InputForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('test.html', form=form)
        else:
            register_no = form.register_no.data
            dob = datetime.datetime.strptime(str(form.dob.data), '%Y-%m-%d').strftime('%d-%m-%Y')
            # return "Form posted {0} {1}".format(register_no, dob)
            # fetch_details(register_no, dob)
            s = Scrapper(register_no, dob)
            json_data = s.get_json()
            return render_template('test.html', form=form, data=json_data)
    elif request.method == 'GET':
        return render_template('test.html', form=form, title='Test Endpoint')