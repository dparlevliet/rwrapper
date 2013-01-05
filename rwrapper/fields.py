import math

def negative_field_check(should_check, value):
  if not should_check:
    return value

  if not isinstance(value, (int, float, long)):
    raise ValueError('%s field is the wrong type. Checked: int, long, float' % self.name)

  if not value < 0:
      raise ValueError('%s field is not a negative value. Value: %r' % (self.name, value))

def positive_field_check(should_check, value):
  if not should_check:
    return value

  if not isinstance(value, (int, float, long)):
    raise ValueError('%s field is the wrong type. Checked: int, long, float' % self.name)

  if not value > 0:
      raise ValueError('%s field is not a positive value. Value: %r' % (self.name, value))


class Field(object):

  __rfield__    = True

  name          = None
  required      = True

  def __init__(self, **kwargs):
    for key in kwargs:
      setattr(self, key, kwargs[key])

  def validate(self, value):
    if value == None and not self.default == False:
      return self.default

    if value == None and self.required == True:
      raise ValueError('%s field is a required field. NoneType found.' % self.name)
    return value


class BooleanField(Field):

  convert_type      = True
  default           = False

  def validate(self, value):
    value = super(BooleanField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, bool):
        raise ValueError('%s field is not String type.' % self.name)
    else:
      if int(value) == 0:
        value = False
      elif int(value) == 1:
        value = True
      else:
        raise ValueError('%s field could not be converted to Boolean. Expected 0 or 1, found: %r'
                    % (self.name, value))

    return value

class CharField(Field):

  convert_type      = True
  max_length        = None
  min_length        = None
  default           = False

  utf8              = True

  def validate(self, value):
    value = super(CharField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, types.StringTypes):
        raise ValueError('%s field is not String type.' % self.name)
    else:
      value = str(value if not self.utf8 else value.encode('utf8'))

    if not self.min_length == None and len(value) < self.min_length:
      raise ValueError('%s field too small. Constrained to maximum %d chars. Currently %d: "%s"'
                    % (self.name, self.min_length, len(value), value))

    if not self.max_length == None and len(value) > self.max_length:
      raise ValueError('%s field too long. Constrained to maximum %d chars. Currently %d: "%s"'
                    % (self.name, self.max_length, len(value),
                          value[:20] + ' [...]' if len (value) > 20 else value))

    return value


class LongField(Field):

  positive_only     = False
  negative_only     = False
  convert_type      = True
  max_digits        = None
  default           = False

  def validate(self, value):
    value = super(LongField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, long):
        raise ValueError('%s field is not Long type.' % self.name)
    else:
      value = long(value)

    negative_field_check(self.negative_only, value)
    positive_field_check(self.positive_only, value)

    if not self.max_digits == None:
      self.max_digits = int(self.max_digits)
      if self.max_digits > 0 and not value < math.pow(10, self.max_digits) and \
                                  not value > -math.pow(10, self.max_digits):
        raise ValueError('%s field size invalid. Constraint: maximum %d digits. Value: %d'
                    % (self.name, self.max_digits))

    return value


class IntegerField(Field):

  positive_only     = False
  negative_only     = False
  convert_type      = True
  max_digits        = None
  default           = False

  def validate(self, value):
    value = super(IntegerField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, int):
        raise ValueError('%s field is not Integer type.' % self.name)
    else:
      value = int(value)

    negative_field_check(self.negative_only, value)
    positive_field_check(self.positive_only, value)

    if not self.max_digits == None:
      self.max_digits = int(self.max_digits)
      if self.max_digits > 0 and not value < math.pow(10, self.max_digits) and \
                                  not value > -math.pow(10, self.max_digits):
        raise ValueError('%s field size invalid. Constraint: maximum %d digits. Value: %d'
                    % (self.name, self.max_digits))

    return value


class FloatField(Field):

  negative_only     = False
  positive_only     = False
  convert_type      = True
  max_digits        = None
  max_decimals      = None
  round_decimals    = False
  default           = False

  def validate(self, value):
    value = super(FloatField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, float):
        raise ValueError('%s field is not Float type.' % self.name)
    else:
      value = float(value)

    negative_field_check(self.negative_only, value)
    positive_field_check(self.positive_only, value)

    if not self.max_digits == None and self.max_digits > 0:
      IntegerField(name=self.name, max_digits=self.max_digits).validate(value)

    # todo: try think of a better way to do this.
    if not self.max_decimals == None and self.round_decimals == False:
      decimals = str(value - int(value))
      if decimals.startswith("0.") and len(decimals[2:]) > self.max_decimals:
        raise ValueError("%s field size invalid. Constraint: maximum %d decimals. Value: %f"
                      % (self.name, self.max_decimals))
    elif not self.max_decimals == None:
      value = round(value, self.max_decimals)

    return value