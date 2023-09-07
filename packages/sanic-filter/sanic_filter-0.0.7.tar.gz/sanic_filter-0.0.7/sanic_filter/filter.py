from sqlalchemy import select, insert, or_, String, cast


class FilterMeta(type):
    """
    Delete required fields from the common pool of variables
    Add meta variable for further query building
    *Add validate options
    """

    def __new__(cls, name, bases, dct):
        if bases:
            attrs = {}
            for name, value in dct.items():
                if isinstance(value, Query):
                    attrs[name] = value.options

            dct['meta'] = attrs
            ann = dct.get('__annotations__')
            new_ann = {}
            for name, value in attrs.items():
                if value.get('required', False):
                    del dct[name]
                    new_ann[name] = ann[name]
                else:
                    dct[name] = None
            new_ann.update(ann)
            dct['__annotations__'] = new_ann
        return type.__new__(cls, name, bases, dct)


class Query:
    """
    option = like, ilike, in, !=, == and returned_fields
    required = True/False
    json = True/False This field is json?
    parent = name of json field id json=True
    """

    def __init__(self, **options):
        self.options = options


class Filter(metaclass=FilterMeta):
    def __new__(cls, *args, **kwargs):
        return FilterBase(meta=cls.meta, fields=kwargs)


class FilterBase:

    def __init__(self, meta, fields=None):
        self.meta = meta
        self.data_fields = {}
        for name, value in fields.items():
            if value != 'None':
                if self.meta.get(name):
                    self.meta[name].update({'value': value})
                self.data_fields[name] = value
            else:
                self.meta[name].update({'value': None})

    def filter(self, query):
        #### if alchemy .....
        return self.__alchemy_filter(query=query)

    def __alchemy_filter(self, query):
        """
        """
        returned = []
        params = []
        models, operator = self.__get_alchemy_models(query)
        for param, options in self.meta.items():
            option = options.get('option')
            value = options.get('value')
            json_column = options.get('json_column')
            if value is None:
                continue
            if option == 'returned_fields':
                if returned:
                    continue
                returned = self.__returned_fields(models=models, value=value)
                continue
            if json_column:
                field = self.__get_json_field(models=models, child=param, parent=json_column)
            else:
                field = self.__get_field(models=models, param=param)
            params = params + self.__create_exp(param=field, values=value, option=option)
        if not returned:
            return query.filter(or_(*params))
        return operator(*returned).filter(or_(*params))

    def __get_alchemy_models(self, query):
        models = {}
        operator = None
        for column in query.column_descriptions:
            models[column.get('name')] = {
                'fields': [name for name, value in column.get('entity').__dict__.items() if
                           not name.startswith('__') and name != '_sa_class_manager'],
                'model': column.get('type'),
            }
        if query.is_select:
            operator = select
        elif query.is_dml:
            operator = insert
        return models, operator

    def __returned_fields(self, models, value):
        returned_fields = []
        fields = value.replace(' ', '').split(',')
        for field in fields:
            parents = field.split('.')
            attr = None
            for name, values in models.items():
                if parents[0] in values.get('fields'):
                    for parent in parents:
                        if attr is None:
                            attr = getattr(values.get('model'), parent)
                        else:
                            attr = attr[parent]
                    returned_fields.append(attr)  # add as
        return returned_fields

    def __get_json_field(self, models, child, parent):
        parents = parent.split('.')
        attr = None
        for name, values in models.items():
            if parents[0] in values.get('fields'):
                for parent in parents:
                    if attr is None:
                        attr = getattr(values.get('model'), parent)
                    else:
                        attr = attr[parent]
                attr = attr[child]
                return attr
                # return cast(attr, String)

    def __get_field(self, models, param):
        for name, values in models.items():
            if param in values.get('fields'):
                attr = getattr(values.get('model'), param)
                return attr

    def __create_exp(self, param, values, option):
        if not values:
            return
        values = values.split(',')
        options = option.replace(' ', '').split(',')
        params = []
        param = cast(param, String)
        buf = None
        for option in options:
            for value in values:
                if not value:
                    continue
                if option == 'like':
                    buf = param.like('{}'.format(value))
                elif option == 'ilike':
                    buf = param.ilike('%{}%'.format(value))
                elif option == 'in':
                    buf = param.in_(values), String
                elif option == '==':
                    buf = param == value
                elif option == '!=':
                    buf = param != value
                elif option == '>=':
                    buf = param >= value
                elif option == '<=':
                    buf = param <= value
                if buf is not None:
                    params.append(buf)
        return params

