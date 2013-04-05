import math


def negative_field_check(should_check, value):
  if not should_check:
    return value

  if not isinstance(value, (int, float, long)):
    raise ValueError('%s field is the wrong type. Checked: int, long, float' % value)

  if not value < 0:
      raise ValueError('%s field is not a negative value' % value)


def positive_field_check(should_check, value):
  if not should_check:
    return value

  if not isinstance(value, (int, float, long)):
    raise ValueError('%s field is the wrong type. Checked: int, long, float' % value)

  if not value > 0:
      raise ValueError('%s field is not a positive value.' % value)


class Field(object):

  __rfield__        = True

  name              = None
  required          = True

  convert_type      = True
  default           = '_rwrapper_default'

  def __init__(self, **kwargs):
    for key in kwargs:
      setattr(self, key, kwargs[key])

  def _name(self):
    return self.name+'.'+self.__class__.__name__

  def validate(self, value):
    if value == None and not self.default == '_rwrapper_default':
      return self.default

    if value == None and self.required == True:
      raise ValueError('%s field is a required field. NoneType found.' % self._name())
    return value

  def ensure_max_digits(self, value):
    if not self.max_digits == None:
      self.max_digits = int(self.max_digits)
      if self.max_digits > 0 and not value < math.pow(10, self.max_digits) and \
                                  not value > -math.pow(10, self.max_digits):
        raise ValueError('%s field size invalid. Constraint: maximum %d digits. Value: %d'
                    % (self._name(), self.max_digits))
    return value

  def ensure_max_decimals(self, value):
    # todo: try think of a better way to do this.
    if not self.max_decimals == None and self.round_decimals == False:
      decimals = str(value - int(value))
      if decimals.startswith("0.") and len(decimals[2:]) > self.max_decimals:
        raise ValueError("%s field size invalid. Constraint: maximum %d decimals. Value: %f"
                      % (self._name(), self.max_decimals))
    elif not self.max_decimals == None:
      value = round(value, self.max_decimals)
    return value

class BooleanField(Field):

  def validate(self, value):
    value = super(BooleanField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, bool):
        raise ValueError('%s field is not String type.' % self._name())
    else:
      if int(value) == 0:
        value = False
      elif int(value) == 1:
        value = True
      else:
        raise ValueError('%s field could not be converted to Boolean. Expected 0 or 1, found: %r'
                            % (self._name(), value))

    return value

class CharField(Field):

  max_length        = None
  min_length        = None

  utf8              = True

  def validate(self, value):
    value = super(CharField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, types.StringTypes):
        raise ValueError('%s field is not String type.' % self._name())
    elif not value == None:
      try:
        value = str(value if not self.utf8 else value.encode('utf8'))
      except:
        raise ValueError('%s field is not a String type.' % self._name())

    if not self.min_length == None and len(value) < self.min_length:
      raise ValueError('%s field too small. Constrained to maximum %d chars. Currently %d: "%s"'
                    % (self._name(), self.min_length, len(value), value))

    if not self.max_length == None and len(value) > self.max_length:
      raise ValueError('%s field too long. Constrained to maximum %d chars. Currently %d: "%s"'
                    % (self._name(), self.max_length, len(value),
                          value[:20] + ' [...]' if len (value) > 20 else value))

    return value


class LongField(Field):

  positive_only     = False
  negative_only     = False
  round_decimals    = True #todo: implement this
  max_digits        = None

  def validate(self, value):
    value = super(LongField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, long):
        raise ValueError('%s field is not Long type.' % self._name())
    elif not value == None:
      try:
        value = long(value)
      except:
        raise ValueError('Error trying to convert %s to Long type.' % self._name())

    negative_field_check(self.negative_only, value)
    positive_field_check(self.positive_only, value)

    return self.ensure_max_digits(value)


class IntegerField(Field):

  positive_only     = False
  negative_only     = False
  max_digits        = None

  def validate(self, value):
    value = super(IntegerField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, int):
        raise ValueError('%s field is not Integer type.' % self._name())
    elif not value == None:
      value = int(value)

    negative_field_check(self.negative_only, value)
    positive_field_check(self.positive_only, value)

    return self.ensure_max_digits(value)


class FloatField(Field):

  negative_only     = False
  positive_only     = False
  max_digits        = None
  max_decimals      = None
  round_decimals    = False

  def validate(self, value):
    value = super(FloatField, self).validate(value)

    if not self.convert_type:
      if not isinstance(value, float):
        raise ValueError('%s field is not Float type.' % self._name())
    elif not value == None:
      value = float(value)

    negative_field_check(self.negative_only, value)
    positive_field_check(self.positive_only, value)

    if not self.max_digits == None and self.max_digits > 0:
      IntegerField(name=self._name(), max_digits=self.max_digits).validate(value)

    return self.ensure_max_decimals(value)