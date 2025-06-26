from marshmallow import Schema, fields, validate

class EpuSchema(Schema):
    contract_number = fields.Str()
    dateInit = fields.Str()
    dateEnd = fields.Str()

class SchemaSearchSp(Schema):
    entidad = fields.Str()
    cen_alt = fields.Str()
    cuenta = fields.Str()