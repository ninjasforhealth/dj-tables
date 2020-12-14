class TableOrderByMixin:
    """
    Allows the ordering of a query to be specified
    by a query parameter.
    """
    order_by_field = 'sort'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by_field'] = self.order_by_field
        context['order_by'] = self.get_ordering()
        return context

    def get_ordering(self):
        order_by = self.request.GET.get(self.order_by_field, None)
        if order_by:
            return order_by
        return super().get_ordering()
