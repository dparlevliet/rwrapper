from rethinkdb import r

class rwrapper(object):

  id            = None

  _limit        = 0
  _order_by     = None
  _meta         = None
  _fmeta        = None

  def __json__(self):
    d = {}
    for key in dir(self):
      try:
        if not key.startswith('_') and not hasattr(getattr(self, key), '__call__'):
          d[key] = getattr(self, key)
      except:
        continue
    return d

  def __getattribute__(self, name):
    if name == '__dict__':
      return self.__json__()
    return object.__getattribute__(self, name)

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
        if value.__rfield__:
          self._meta[key] = value
        else:
          self._fmeta[key] = value
        self._meta[key].name = key
        setattr(self, key, None)
      except:
        continue
    for key in kwargs:
      setattr(self, key, kwargs[key])

  def evaluate_insert(self, result):
    if result['errors']>1:
      raise IOError(result)
    elif result['inserted'] == 1:
      self.id = result['generated_keys'][0]
    return self.id

  def evaluate_update(self, result):
    if result['updated'] == 0:
      raise ValueError(result)
    if result['errors'] > 0:
      raise IOError(result)
    return result

  def rq(self, filter=False):
    if not filter:
      filter = self._filter()
    rq = r.table(self._db_table)
    if len(filter)>0:
      rq = rq.filter(filter)
    if not self._order_by == None:
      rq = rq.order_by(*tuple([order if not order[:1] == '-' else r.desc(order[1:]) for order in list(self._order_by) ]))
    if not self._limit == 0:
      rq = rq.limit(int(self._limit))
    return rq

  def _filter(self):
    filter = {}
    for key, value in self.__dict__.iteritems():
      if not value == None:
        filter[key] = value
    return filter

  def order_by(self, *args):
    self._order_by = args
    return self

  def limit(self, amount):
    self._limit = amount
    return self

  def save(self):
    doc = self.__dict__
    # do any field validation
    if len(self._meta) > 0:
      for key in self._meta.keys():
        setattr(self, key, self._meta[key].validate(doc[key]))

    # id being none means we should insert
    if self.id == None:
      if 'id' in doc:
        del doc['id']
      return self.evaluate_insert(r.table(self._db_table).insert(doc).run())

    # id found; update
    return self.evaluate_update(r.table(self._db_table).filter({'id': self.id}).update(self._filter()).run())

  def count(self, filter=False):
    return self.rq(filter).count().run()

  def get(self, o=False, exception=False):
    try:
      result = self.rq().limit(1).run()[0]
      return result if o == False else o(**result)
    except:
      if exception == False:
        return None
      raise ValueError

  def all(self, o=False):
    return [ row if o == False else o(**row) for row in self.rq().run() ]

  def delete(self, filter=False):
    return self.rq(filter).delete().run()
