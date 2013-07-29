#! /usr/bin/python
"""
@fileoverview CRUD example
@author David Parlevliet
@version 20130730
@preserve Copyright 2013 David Parlevliet.

CRUD Example
============
Useful for understanding how rWrapper works. But, also doubles as a testing
script.
"""
import rethinkdb as r
from rwrapper import rwrapper, fields

conn = r.connect(
  host='localhost', 
  port=29015, 
  db='rwrapper'
).repl()

try:
  r.db_drop('rwrapper').run()
except:
  pass

r.db_create('rwrapper').run()
r.table_create('test_1').run()

class MyTable(rwrapper):
  _db_table = 'test_1'
  field1 = fields.CharField()
  field2 = fields.CharField()

def main():
  create = MyTable( 
    field1='something', 
    field2='something else'
  )
  # C
  create.save()
  print "Inserted new row: %s" % create.id

  # R
  read = MyTable(id=create.id).get()
  print "Reading data for %s: %s" % ( create.id, read)

  # U
  update = MyTable(id=create.id).get(MyTable)
  update.field1 = 'something new'
  update.save()
  print "Updating data for: %s" % create.id

  read = MyTable(id=create.id).get()
  print "New data for %s: %s" % ( create.id, read)

  # D
  delete = MyTable(id=create.id).delete()
  print "Deleted %s" % create.id

if __name__ == '__main__':
  main();