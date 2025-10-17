from marshmallow import Schema, fields, validate, pre_load

class UserRegisterSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=50)
    )
    email = fields.Email(
        required=True,
        validate=validate.Length(max=100)
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128)
    )

    @pre_load
    def normalise_input(self, data, **kwargs):
        """Normalise whitespace + casing before validation."""
        if "username" in data and data["username"]:
            data["username"] = data["username"].strip()
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower().strip()
        return data

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
