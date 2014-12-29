from flask.ext.wtf import Form
from wtforms import StringField, DateField, validators


class InputForm(Form):
    register_no = StringField(
        label='Register No',
        validators=[validators.DataRequired(message='Register number required.'),
                    validators.Length(min=8, max=20),
        ]
    )
    dob = DateField(
        label='Date of Birth',
        format="%d-%m-%Y",
        validators=[validators.DataRequired(message='Date of Birth required.')]
    )
