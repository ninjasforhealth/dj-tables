from django.template import Context, Template
from django.test import TestCase

from lxml import html


_test_data = [
    {'first_name': 'John', 'last_name': 'Doe', 'favorite_foods': ['Pizza', 'French Fry'],},
    {'first_name': 'Jane', 'last_name': 'Doe', 'favorite_foods': ['Burger', 'Chicken'],},
    {'first_name': 'Zach', 'last_name': 'Perkitny', 'favorite_foods': ['Egg', 'Salmon'],},
]


class TableNodeTest(TestCase):
    def test_render(self):
        template = Template('''
            {% load dj_tables %}
            {% table data %}
                {% tableheader key='first_name' %}
                {% tableheader key='last_name' %}
            {% endtable %}
        ''')
        tree = html.fromstring(template.render(Context({
            'data': _test_data,
        })))

        self.assertEqual(len(tree.xpath('.//thead/tr/th')), 2)
        self.assertEqual(len(tree.xpath('.//tbody/tr')), 3)
        self.assertEqual(len(tree.xpath('.//tbody/tr/td')), 6)

    def test_IfNode_render(self):
        template = Template('''
            {% load dj_tables %}
            {% table data %}
                {% tableheader key='first_name' %}
                {% if show_last_name %}
                {% tableheader key='last_name' %}
                {% endif %}
            {% endtable %}
        ''')
        tree = html.fromstring(template.render(Context({
            'data': _test_data,
            'show_last_name': False,
        })))

        # Last Name header should not be rendered
        self.assertEqual(len(tree.xpath('.//thead/tr/th')), 1)
        # Row also should not render last name column
        self.assertEqual(len(tree.xpath('.//tbody/tr[1]/td')), 1)

    def test_TableHeader_content_render(self):
        template = Template('''
            {% load dj_tables %}
            {% table data %}
                {% tableheader text='Name' %}
                    <span>{{ tablerow.first_name }} {{ tablerow.last_name }}</span>
                {% endtableheader %}
            {% endtable %}
        ''')
        tree = html.fromstring(template.render(Context({
            'data': _test_data,
        })))

        # Should render the contents of tableheader
        self.assertTrue(len(tree.xpath('./tbody/tr/td[1]/span')), 3)

    def test_RowAction_render(self):
        template = Template('''
            {% load dj_tables %}
            {% table data %}
                {% tableheader key='first_name' %}
                {% tableheader key='last_name' %}
                {% tablerowaction view='test' classname='fa fa-something' %}
            {% endtable %}
        ''')
        tree = html.fromstring(template.render(Context({
            'data': _test_data,
        })))

        # Should add column for actions
        self.assertEqual(len(tree.xpath('./thead/tr/th')), 3)
        # Should render the icon with the provided class name
        self.assertEqual(
            len(tree.xpath('./tbody/tr/td[3]//i[contains(@class, "fa fa-something")]')), 3)

    def test_SubTable_render(self):
        template = Template('''
            {% load dj_tables %}
            {% table data %}
                {% tableheader key='first_name' %}
                {% tableheader key='last_name' %}
                {% subtable %}
                    {% table tablerow.favorite_foods %}
                        {% tableheader key='0' text='Name' %}
                    {% endtable %}
                {% endsubtable %}
            {% endtable %}
        ''')
        tree = html.fromstring(template.render(Context({
            'data': _test_data,
        })))

        # Should add column for collapsible toggle
        self.assertEqual(len(tree.xpath('./thead/tr/th')), 3)
        # Should add a row for each subtable
        self.assertEqual(len(tree.xpath('./tbody/tr')), 6)
        # Should render the contents of subtable
        self.assertTrue(
            len(tree.xpath('./tbody/tr[position() mod 2 = 0]//table')), 3)


class TableHeaderNodeTest(TestCase):
    def test_render(self):
        template = Template('''
            {% load dj_tables %}
            {% tableheader key='test1' %}
            {% tableheader key='test2' %}
            {% tableheader key='test3' %}
        ''')

        tableheaders = []
        template.render(Context({
            'tableheaders': tableheaders,
        }))

        # Should push into the tableheaders list in the
        # current template context
        self.assertEqual(len(tableheaders), 3)

    def test_NodeList_render(self):
        template = Template('''
            {% load dj_tables %}
            {% tableheader text='Life' %}
                42
            {% endtableheader %}
        ''')

        tableheaders = []
        template.render(Context({
            'tableheaders': tableheaders,
        }))

        # Should add the nodelist and render context to its data dictionary
        self.assertIsNotNone(tableheaders[0].get('nodelist'))
        self.assertIsNotNone(tableheaders[0].get('render_context'))


class TableRowActionNodeTest(TestCase):
    def test_render(self):
        template = Template('''
            {% load dj_tables %}
            {% tablerowaction view='test' classname='fa fa-something' %}
            {% tablerowaction view='test' classname='fa fa-pencil' %}
            {% tablerowaction view='test' classname='fa fa-trash' %}
        ''')

        tablerowactions = []
        template.render(Context({
            'tablerowactions': tablerowactions,
        }))

        # Should push into tablerowactions list in the
        # current template context
        self.assertEqual(len(tablerowactions), 3)


class SubtableNodeTest(TestCase):
    def test_render(self):
        template = Template('''
            {% load dj_tables %}
            {% subtable %}
                Hello world
            {% endsubtable %}
            {% subtable %}
                Whatever you want here
            {% endsubtable %}
        ''')

        subtables = []
        template.render(Context({
            'subtables': subtables,
        }))

        # Should push into subtables list in the
        # current template context
        self.assertEqual(len(subtables), 2)
