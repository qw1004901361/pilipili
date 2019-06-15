# coding=UTF-8
from flask import request
from wtforms import Form

from app.libs.error_code import ParameterException


class BaseForm(Form):

    def __init__(self):
        if request.form:
            data = request.form
        elif request.get_json(silent=True):
            data = request.get_json(silent=True)
        else:
            data = request.args
        super(BaseForm, self).__init__(formdata=data)

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self
