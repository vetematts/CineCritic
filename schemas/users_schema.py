from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
