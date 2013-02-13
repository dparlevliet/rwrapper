RethinkDB Python Wrapper Class
==============================
Since I've been using Django a lot recently I've become sort of spoiled by the
Database abstraction that comes with it, but unfortunately using that with RDB
just isn't an option so I tried to find a nice middle ground. This wrapper
allows me to emulate the most common usages from Django's DB abstraction -- for
anything more complex I believe it would be best to do a manual query.

Related post: http://c2journal.com/2012/12/29/making-a-wrapper-for-your-rethinkdb-tables-in-python/


Author's note
=============
Do not use this wrapper class if you are worried about saving every possible
millisecond. Keep in mind, that while it is small it will still add weight and
processing time to your application. For HTTP response queries, where possible,
always use direct queries -- especially if it is a merely to fetch and return
row(s). I recommend trying to use this wrapper for save/updated or in a threaded
process.


Class Examples
==============
###### Example Table #1
```
class MyTable(rwrapper):
  field1 = None
  field2 = None
  _db_table = 'my_table'
```
###### Example Table #2
```
class MyTable(rwrapper):
  field1 = CharField()
  field2 = CharField()
  _db_table = 'my_table'
```
###### Example Table #3
```
class MyTable(rwrapper):
  field1 = FloatField(max_decimals=2, round_decimals=True)
  field2 = CharField()
  _db_table = 'my_table'
```

Field Types
===========
##### Global Options
These options are available to every field type.
```
Param           Default       Description
=========================================
required        True          Is this field required for every entry?
convert_type    True          Should the field controller should try to convert the type for consistency?

```
###### BooleanField
```
* Global Options only
```
###### CharField
```
Param           Default       Description
=========================================
max_length      None          The maximum number of characters this field should store.
min_length      None          The minimum number of characters this field should store.
utf8            True          Should this field try to enforce utf8 conversion?
```
###### LongField
```
Param           Default       Description
=========================================
positive_only   False         Should this field contain positive values only?
negative_only   False         Should this field contain negative values only?
max_digits      None          The maximum number of digits this field should have.
```
###### IntegerField
```
* Same as LongField
```
###### FloatField
```
Param           Default       Description
=========================================
positive_only   False         Should this field contain positive values only?
negative_only   False         Should this field contain negative values only?
max_digits      None          The maximum number of digits this field should have.
max_decimals    None          The maximum number of decimal places this field should have.
round_decimals  False         Should this field be rounded to the max_decimal length?
```


Save Documents
==============
```
save([object=False])
```
<tt>save()</tt> is responsible for new record creation and updating existing records

### Examples

#### new document
```
table = MyTable(field1='something', field2='something else')
table.save()
```
After <tt>save()</tt> will update the <tt>id</tt> field to reflect the id of the newly generated document.

#### update document
```
# if the id field is set, the class will attempt to update
table = MyTable(id=1, field1='something new')
table.save()
```
Note: <tt>save()</tt> will only update if the fields ACTUALLY change, otherwise it will not bother trying.

Get Documents
=============
```
all([object=False])
get([object=False, [return_exception=False]])
```
<tt>all()</tt> Will will return every result found.
<tt>get()</tt> Will append .limit(1) to any query and attempt to return the result.

### Examples

#### get documents
```
table = MyTable(field1='something')
results = table.all()
```
This will return a list containing the dictionary response for each document. Which means, that if you needed to json
serialize the return you do not need to loop the records, you can simply do: <tt>json.dumps(results)</tt>

This is the same as running <tt>[row for row in results]</tt>

#### get documents as an object list
```
table = MyTable(field1='something')
results = table.all(MyTable)
```
This will return a list containing the passed object with the response data already parsed. You cannot json serialize
this type of call.

This is the same as running <tt>[MyTable(**row) for row in results]</tt>

#### get document record
```
table = MyTable(id=1)
result = table.get()
```
This will return the first record from a query. This is the same as running <tt>result[0]</tt>. In this instance, 
if 0 index is not found then None is returned.

Count Documents
===============
```
table = MyTable(field1='something')
count = table.count()
```

Delete Documents
================
```
table = MyTable(field1='something')
result = table.delete()
```

Order Documents
===============
#### Ascending
```
table = MyTable(field1='something')
results = table.order_by('field1').all()
```
#### Descending
```
table = MyTable(field1='something')
results = table.order_by('-field1').all()
```

Usage with jsonpickle
=====================
This example assumes the existance of a common.py, you will have to adjust it to 
suit your project. This is useful when working with Celery/RabbitMQ.

###### utils/common.py
```
import jsonpickle


def pickle(arg):
  if hasattr(arg, '_pickle'):
    arg._pickle = True
  return jsonpickle.encode(arg)


def depickle(arg):
  arg = jsonpickle.decode(arg)
  if hasattr(arg, '_pickle'):
    arg._pickle = False
  return arg
```

###### All other files where jsonpickle is needed for rwrapper
```
from utils.common import pickle
from utils.common import depickle

def method1():
  return method2(pickle(obj))

def method2(obj):
  return depickle(obj)
```
