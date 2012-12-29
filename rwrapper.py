from rethinkdb import r

class rwrapper():

  _order_by = None

  def __init__(self, **kwargs):
    for key in kwargs:
      setattr(self, key, kwargs[key])

  def evaluate_insert(self, result):
    if result['errors']>1:
      raise IOError
    elif result['inserted'] == 1:
      self.id = result['generated_keys'][0]
    return self.id

  def evaluate_update(self, result):
    if result['updated'] == 0:
      raise ValueError
    if result['errors'] > 0:
      raise IOError
    return update

  def rq(self, filter=False):
    if not filter:
      filter = self._filter()
    rq = r.table(self._db_table)
    if len(filter)>0:
      rq = rq.filter(filter)
    if not self._order_by == None:
      rq = rq.order_by(*tuple([order if not order[:1] == '-' else r.desc(order[1:]) for order in list(self._order_by) ]))
      pass
    return rq

  def _filter(self):
    filter = {}
    for attr in self.__dict__.keys():
      if attr[:1] == '_': # double check they're not private
        continue
      val = self.__dict__[attr]
      if not val == None:
        filter[attr] = val
    return filter

  def order_by(self, *args):
    self._order_by = args
    return self

  def save(self):
    if self.id == None:
      return self.evaluate_insert(r.table(self._db_table).insert(self.__dict__).run())
    return self.evaluate_update(self.rq().update(self._filter()).run())

  def count(self, filter=False):
    return self.rq(filter).count().run()

  def get(self, object=False, exception=False):
    try:
      result = self.rq().run()[0]
      return result if object == False else object(**result)
    except:
      if exception == False:
        return None
      raise ValueException

  def all(self, object=False):
    return [ row if object == False else object(**row) for row in self.rq().run() ]

  def delete(self, filter=False):
    return self.rq(filter).delete().run()

