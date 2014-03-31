RethinkDB Python ORM
====================
This ORM allows you to emulate the most common usages from Django's DB abstraction. For
anything more complex I believe it would be best to do a manual query.

Related posts
  * http://c2journal.com/2012/12/29/making-a-wrapper-for-your-rethinkdb-tables-in-python/
  * http://c2journal.com/2013/03/25/django-and-rethinkdb-a-tutorial/

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
###### ObjectField
```
* Global Options only
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

#### v1.4 update
Version 1.4 changed the way that RethinkDB connections are handled. They're no longer discovered unless 
you use <tt>repl()</tt> on your connection. All examples below assume that you haven't used <tt>repl()</tt>.

#### preparation
```
import rethinkdb as r
conn = r.connect(host='localhost', port=29015, db='rwrapper')
```

#### new document
```
table = MyTable(_connection=conn, field1='something', field2='something else')
table.save()
```
After <tt>save()</tt> will update the <tt>id</tt> field to reflect the id of the newly generated document.

#### update document
```
# if the id field is set, the class will attempt to update
table = MyTable(_connection=conn, id=1, field1='something new')
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
table = MyTable(_connection=conn, field1='something')
results = table.all()
```
This will return a list containing the dictionary response for each document. Which means, that if you needed to json
serialize the return you do not need to loop the records, you can simply do: <tt>json.dumps(results)</tt>

This is the same as running <tt>[row for row in results]</tt>

#### get documents as an object list
```
table = MyTable(_connection=conn, field1='something')
results = table.all(MyTable)
```
This will return a list containing the passed object with the response data already parsed. You cannot json serialize
this type of call.

This is the same as running <tt>[MyTable(**row) for row in results]</tt>

#### get document record
```
table = MyTable(_connection=conn, id=1)
result = table.get(dict)
```
This will return the first record from a query as a dictionary. This is the same as running <tt>dict(result[0])</tt>. In this instance, 
if 0 index is not found then None is returned.

This is useful if you want to return JSON data

#### get document record as cursor
```
table = MyTable(_connection=conn, id=1)
result = table.get()
```
This will return the first record from a query. This is the same as running <tt>result[0]</tt>. In this instance, 
if 0 index is not found then None is returned.

Count Documents
===============
```
table = MyTable(_connection=conn, field1='something')
count = table.count()
```

Delete Documents
================
```
table = MyTable(_connection=conn, field1='something')
result = table.delete()
```

Order Documents
===============
#### Ascending
```
table = MyTable(_connection=conn, field1='something')
results = table.order_by('field1').all()
```
#### Descending
```
table = MyTable(_connection=conn, field1='something')
results = table.order_by('-field1').all()
```

Accessing Object JSON properties
================================
For use with CRUD you will often want to access the dictionary table form to return. Here are semi-real examples.

###### Example 1
```
table = MyTable(_connection=conn, field1='something')
table.save()
return json.dumps(table.__dict__)
```

###### Example 2
```
table = MyTable(_connection=conn, id='something').get(dict)
return json.dumps(table)
```

###### Example 3
```
table = MyTable(_connection=conn, id='something').get(MyTable)
if table.field1 == 'something':
  return json.dumps(table.__dict__)
```


Private variables
=================
Any variable that you do not wish to be saved, or returned can be set as a private variable by appending _ to the variable name.
###### Example
```
table = MyTable(_connection=conn)
table._my_private_variable = 'something too awesome to share!'
```
#### Reserved private variables
```
Param           Default       Description
=========================================
_limit          0             Used when defining whether to limit a query
_order_by       None          Used when definiting whether to order a query
_meta           None          Used for storing initial field object data (if any)
_changed        False         Used to determine whether the object has changed and should be saved
_pickle         False         Used when defining if pickle support is needed (see pickling)
_connection     None          Used for accessing the passed connection object (if any)
_upsert         False         Specifies whether save() should perform an upsert
_non_atomic     True          Specifies whether updates should be atomic or non-atomic (http://en.wikipedia.org/wiki/Atomic_operation)
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
