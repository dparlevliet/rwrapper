RethinkDB Python Wrapper Class
==============================
Since I've been using Django a lot recently I've become sort of spoiled by the
Database abstraction that comes with it, but unfortunately using that with RDB
just isn't an option so I tried to find a nice middle ground. This wrapper
allows me to emulate the most common usages from Django's DB abstraction -- for
anything more complex I believe it would be best to do a manual query.

Related post: http://c2journal.com/2012/12/29/making-a-wrapper-for-your-rethinkdb-tables-in-python/

Usage
=====
```
class MyTable(rwrapper):
  id     = None
  field1 = None
  field2 = None

# new document
table = MyTable(field1='something', field2='something else')
table.save()

# update document
# if the id field is set, the class will attempt to update
table = MyTable(id=1, field1='something new')
table.save()

# get documents
table = MyTable(field1='something')
results = table.all()

# get document record
table = MyTable(id=1)
result = table.get()

# count documents
table = MyTable(field1='something')
count = table.count()

# delete document
table = MyTable(field1='something')
result = table.delete()

# order by ascending
table = MyTable(field1='something')
results = table.order_by('field1').all()

# order by descending
table = MyTable(field1='something')
results = table.order_by('-field1').all()
```