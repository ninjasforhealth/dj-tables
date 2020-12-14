# dj-tables
A template only and DRY solution for creating tables.

Specifying how data is displayed should be exclusively done by the template, and this library
aims to do this by providing powerful template tags for constructing complex tables.

The full documentation is available [on Read the Docs](https://dj-tables.readthedocs.io/).

## Installation
Install the package using `pip`:
```
pip install dj-tables
```

Add `dj_tables` to your `INSTALLED_APPS`:
```python
INSTALLED_APPS =(
    # ...
    'dj_tables',
    # ...
)
```

## Basic Example
We start with this basic model:
```python
class MyModel(Model):
    my_field = CharField()
    some_other_field = IntegerField()
```

and this generic `ListView`:
```python
class MyListView(ListView):
    model = MyModel
    template_name = 'some_template.html'
```

And creating the table in your template is straightfoward, add a few tableheader tags with the
attributes you want to be rendered.
```
{% load dj_tables %}
{% table object_list %}
    {% tableheader key='my_field' %}
    {% tableheader key='some_other_field' %}
{% endtable %}
```
