from rethinkdb import r
import json

class rwrapper(object):

  id            = None

  _limit        = 0
  _order_by     = None
  _meta         = None
  _changed      = False
  _pickle       = False


  def __init__(self, **kwargs):
    self._meta = {}
    self._fmeta = {}
    for key in dir(self):
      try:
        if key.startswith('_'):
          continue
        value = getattr(self, key)
        if not value.__rfield__ and not value.__rffield__:
          continue
        self._meta[key] = value
        self._meta[key].name = key
        default = None
        if not value.default == '_rwrapper_default':
          default = value.default
        setattr(self, key, default)
      except:
        continue
    for key in kwargs:
      setattr(self, key, kwargs[key])


  def __json__(self):
    d = {}
    for key in dir(self):
      try:
        if not key == None and not key.startswith('_') and \
                                    not hasattr(getattr(self, key), '__call__'):
          d[key] = getattr(self, key)
      except:
        continue
    return d


  def __setattr__(self, name, value):
    try:
      if not name.startswith('_') and not value == getattr(self, name):
        self._changed = True
    except:
      pass
    return object.__setattr__(self, name, value)


  def __getattribute__(self, name):
    if name == '__dict__':
      if not self._pickle:
        return self.__json__()
    return object.__getattribute__(self, name)


  def evaluate_insert(self, result):
    if result['errors']>1:
      raise IOError(json.dumps(result))
    elif result['inserted'] == 1:
      self.id = result['generated_keys'][0]
    return self.id


  def evaluate_update(self, result):
    if result['updated'] == 0:
      raise ValueError(json.dumps(result))
    if result['errors'] > 0:
      raise IOError(json.dumps(result))
    return result


  def rq(self, filter=False):
    if not filter:
      filter = self._filter()
    rq = r.table(self._db_table)
    if len(filter)>0:
      rq = rq.filter(filter)
    if not self._order_by == None:
      rq = rq.order_by(*tuple([order if not order[:1] == '-' else \
                        r.desc(order[1:]) for order in list(self._order_by) ]))
    if not self._limit == 0:
      rq = rq.limit(int(self._limit))
    return rq


  def _filter(self):
    filter = {}
    for key, value in self.__dict__.iteritems():
      if key in self._meta and self._meta[key].default == value:
        continue
      if not value == None:
        filter[key] = value
    return filter


  def get(self, o=False, exception=False):
    try:
      result = self.rq().limit(1).run()[0]
      result = result if o == False else o(**result)
      if o:
        result.changed(False)
      return result
    except:
      if exception == False:
        return None
      raise ValueError('Row not found in table.')


  def save(self):
    # Try and be lazy about saving. Only save if our values have actually
    # changed
    if not self._changed:
      return False

    # Validate any defined fields and set any defaults
    doc = self.__dict__
    if isinstance(self._meta, dict) and len(self._meta) > 0:
      for key in self._meta.keys():
        setattr(self, key, self._meta[key].validate(doc[key]))

    # id being none means we should insert
    if self.id == None:
      if 'id' in doc:
        del doc['id']
      self.changed(False)
      return self.evaluate_insert(r.table(self._db_table).insert(doc).run())

    # id found; update
    self.changed(False)
    return self.evaluate_update(r.table(self._db_table).filter({'id': self.id})\
                .update(self.__dict__).run())


  def changed(self, value):
    if value == True or value == False:
      self._changed = False
    return self


  def order_by(self, *args):
    self._order_by = args
    return self


  def limit(self, amount):
    self._limit = amount
    return self


  def count(self, filter=False):
    return self.rq(filter).count().run()


  def all(self, o=False):
    return [ row if o == False else o(**row) for row in self.rq().run() ]


  def delete(self, filter=False):
    return self.rq(filter).delete().run()
