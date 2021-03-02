import uuid

from django import template
from django.template.base import (
    Node, TemplateSyntaxError, token_kwargs, Variable, NodeList
)
from django.template.loader import get_template
from django.urls import reverse


register = template.Library()


@register.filter()
def get_item(obj, key):
    return obj.get(key, '')


@register.filter()
def get_attr_or_item(obj, key):
    if hasattr(obj, key):
        return getattr(obj, key)
    elif key in obj:
        return obj[key]
    else:
        return ''


@register.simple_tag()
def tablerowaction_url(obj, viewname, arg_names):
    args = []
    if arg_names:
        for arg in arg_names:
            attr = getattr(obj, arg)
            if callable(attr):
                args.append(attr())
            else:
                args.append(attr)
    return reverse(viewname, args=args)


@register.simple_tag(takes_context=True)
def render(context, renderable, render_context):
    with context.render_context.push(render_context):
        return renderable.render(context)


@register.tag('table_sortlink')
class TableSortLinkNode(Node):
    def __init__(self, parser, token):
        bits = token.split_contents()[1:]
        self.kwargs = token_kwargs(bits, parser)
        for key in self.kwargs:
            if key not in ('key', 'templatename', 'text',):
                raise TemplateSyntaxError(
                    "'table_sortlink' received invalid key: %s" % key)

    def render(self, context):
        key = self.kwargs.get('key')
        if key is None:
            return ''
        key = key.resolve(context)

        text = self.kwargs.get('text')
        if text:
            text = text.resolve(context)
        else:
            text = key.replace('_', ' ').title()

        template_name = self.kwargs.get('templatename')
        if template_name:
            template_name = template_name.resolve(context)
        else:
            template_name = 'dj_tables/bootstrap4_sortlink.html'
        template = get_template(template_name)

        ordering = None
        order_by = context.get('order_by')
        if order_by:
            if isinstance(order_by, str):
                order_by = (order_by,)
            if key in order_by:
                ordering = 'asc'
                key = '-%s' % key
            elif '-%s' % key in order_by:
                ordering = 'desc'

        order_by_field = context.get('order_by_field')
        request = context.get('request')
        url = '?%s=%s' % (order_by_field, key)
        params = request.GET.copy()
        if order_by_field in params:
            del params[order_by_field]
        if params:
            url += '&' + params.urlencode()

        with context.push(ordering=ordering, text=text, url=url):
            return template.render(context.flatten())


@register.tag('table')
class TableNode(Node):
    """
    Allows easy construction of complex tables.

    {% table 'object_list' %}
        {% tableheader attr='attribute' text='Display Name' %}
        {% tableheader attr='attribute2' sortable=True %}
        {% if some_condition %}
        {% tableheader attr='conditional_header' %}
        {% endif %}
    {% endtable %}
    """

    def __init__(self, parser, token):
        bits = token.split_contents()
        bits.pop(0)
        if len(bits) == 0:
            raise TemplateSyntaxError("'table' statement takes one argument")

        self.data = Variable(bits.pop(0))

        self.kwargs = token_kwargs(bits, parser)
        for key in self.kwargs:
            if key not in ('collapseclass', 'templatename', 'subtabletoggletext'):
                raise TemplateSyntaxError(
                    "'table' received invalid key: %s" % key)

        self.nodelist = parser.parse(('endtable',))
        parser.delete_first_token()

    def render(self, context):
        request = context.get("request")

        data = self.data.resolve(context)

        collapseclass = self.kwargs.get('collapseclass')
        if collapseclass:
            collapseclass = collapseclass.resolve(context)

        template_name = self.kwargs.get('templatename')
        if template_name:
            template_name = template_name.resolve(context)
        else:
            template_name = 'dj_tables/bootstrap4.html'
        template = get_template(template_name)

        subtable_toggle_text = self.kwargs.get('subtabletoggletext')
        if subtable_toggle_text:
            subtable_toggle_text = subtable_toggle_text.resolve(context)
        else:
            subtable_toggle_text = 'View Details'

        with context.push(
                tableid=uuid.uuid4(), # just some unique id for the table, useful for bootstrap collapsibles ie.
                tabledata=data,
                tableheaders=[],
                tablerowactions=[],
                subtabletoggletext=subtable_toggle_text,
                subtables=[]):
            self._render_nodelist(self.nodelist, context)

            context['collapseclass'] = collapseclass

            tablecolspan = len(context['tableheaders'])
            if context['tablerowactions']:
                tablecolspan += 1
            if context['subtables']:
                tablecolspan += 1
            context['tablecolspan'] = tablecolspan

            return template.render(context.flatten())

    def _render_nodelist(self, nodelist, context):
        for node in nodelist:
            if self._can_render_node(node):
                node.render(context)
            elif hasattr(node, 'conditions_nodelists'):
                node.conditions_nodelists = [
                    (condition, NodeList([node for node in nodelist if self._can_render_node(node)]))
                    for condition, nodelist in node.conditions_nodelists
                ]
                node.render(context)
            elif hasattr(node, 'nodelist'):
                node.nodelist = NodeList([
                    node for node in node.nodelist if self._can_render_node(node)
                ])
                node.render(context)

    def _can_render_node(self, node):
        return isinstance(node, TableHeaderNode) or\
            isinstance(node, TableRowActionNode) or\
            isinstance(node, SubtableNode)


@register.tag('tableheader')
class TableHeaderNode(Node):
    """
    Adds a tableheader into the current template context. These
    are rendered by the template in the 'table' tag.

    {% tableheader key='some_attr' %}
    {% tableheader key='some_attr' text='Display Text' %}
    {% tableheader key='some_attr' text='Display Text' sortable=True %}
    """

    def __init__(self, parser, token):
        bits = token.split_contents()[1:]
        self.kwargs = token_kwargs(bits, parser)
        for key in self.kwargs:
            if key not in ('key', 'text', 'sortable', 'container_classname',):
                raise TemplateSyntaxError(
                    "'tableheader' received invalid key: %s" % key)

        if not self.kwargs.get('key'):
            self.nodelist = parser.parse(('endtableheader',))
            parser.delete_first_token()
        else:
            self.nodelist = None

    def render(self, context):
        key = self.kwargs.get('key')
        if key:
            key = key.resolve(context)

        text = self.kwargs.get('text')
        if text is None:
            if key:
                text = key.replace('_', ' ').title()
            else:
                text = ''
        else:
            text = text.resolve(context)

        sortable = self.kwargs.get('sortable')
        if sortable is None:
            sortable = False
        else:
            sortable = sortable.resolve(context)

        container_classname = self.kwargs.get('container_classname')
        if container_classname:
            container_classname = container_classname.resolve(context)

        context['tableheaders'].append({
            'container_classname': container_classname,
            'key': key,
            'nodelist': self.nodelist,
            'render_context': context.render_context.dicts[-1],
            'text': text,
            'sortable': sortable,
        })

        return ''


@register.tag('tablerowaction')
class TableRowActionNode(Node):
    """
    Adds a tablerowaction to the current template context. These
    are rendered by the template in the 'table' tag.

    {% tablerowaction view='some_view' classname='fa fa-something' %}
    {% tablerowaction view='some_view' args='id' classname='fa fa-edit' %}
    """

    def __init__(self, parser, token):
        bits = token.split_contents()[1:]
        self.kwargs = token_kwargs(bits, parser)
        for key in self.kwargs:
            if key not in ('view', 'args', 'classname', 'text', 'addnextparam',):
                raise TemplateSyntaxError(
                    "'tablerowaction' received invalid key: %s" % key)

    def render(self, context):
        view = self.kwargs.get('view')
        if view is None:
            return ''
        view = view.resolve(context)

        args = self.kwargs.get('args')
        if args:
            args = args.resolve(context).split(' ')

        classname = self.kwargs.get('classname')
        if classname:
            classname = classname.resolve(context)

        text = self.kwargs.get('text')
        if text:
            text = text.resolve(context)

        addnextparam = self.kwargs.get('addnextparam', False)

        context['tablerowactions'].append({
            'view': view,
            'args': args,
            'classname': classname,
            'text': text,
            'addnextparam': addnextparam,
        })

        return ''


@register.tag('subtable')
class SubtableNode(Node):
    """
    Adds a subtable to the current template context. These
    are rendered by the template in the 'table' tag.

    {% subtable %}
        <h2>
            Wow access to loop context {{ forloop.counter }},
            and the row {{ tablerow.some_attr }}
        </h2>
        <div>Whatever you want in here</div>
    {% endsubtable %}
    """

    def __init__(self, parser, token):
        self.nodelist = parser.parse(('endsubtable',))
        parser.delete_first_token()

    def render(self, context):
        context['subtables'].append({
            'nodelist': self.nodelist,
            'render_context': context.render_context.dicts[-1],
        })
        return ''
