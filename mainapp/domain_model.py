import datetime
from django.db import models
from django.core import serializers
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import WeldData


class Field(models.Field):
    """base class for custom fields"""

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 100
        super().__init__(*args, **kwargs)

    def bind_name(self, name):
        self.name = name
        self.storage_name = ''.join(('_', self.name))
        return self

    def bind_model_cls(self, model_cls):
        self.model_cls = modl_cls
        return self

    def init_model(self, model, value):
        self.set_value(model, value)

    def get_value(self, model):
        return getattr(model, self.storage_name)

    def set_value(self, model, value):
        setattr(model, self.storage_name, self.__converter(value))

    def get_builtin_type(self, model):
        return self.get_value(model)

    def __converter(self, value):
        return value

    @staticmethod
    def _get_model_instance(model_cls, data):
        return model_cls(**data) if isinstance(data, dict) else data


class Bool(Field):
    def __converter(self, value):
        return bool(value)


class String(Field):
    def __converter(self, value):
        return str(value)


class Date(Field):
    def __converter(self, value):
        if not instance(value, datetime.date):
            raise TypeError('{} is not valid date'.format(value))
        return value


class Int(Field):
    def __converter(self, value):
        return int(value)


class Float(Field):
    def __converter(self, value):
        return float(value)


class Model(Field):
    def __init__(self, related_model_cls):
        super().__init__()
        self.related_model_cls = related_model_cls

    def __converter(self, value):
        return self._get_model_instance(self.related_model_cls, value)

    def get_builtin_type(self, model):
        return self.get_value(model).get_data()


class FieldCollection(Field):
    def __init__(self, related_model_cls):
        super().__init__()
        self.related_model_cls = related_model_cls

    def get_builtin_type(self, model):
        return [
            item.get_data()
            if isinstance(item, self.related_model_cls) else item
            for item in self.get_value(model)
        ]


class DomainModelMetaClass(type):
    def __new__(cls, class_name, bases, attributes):
        """this is class factory"""
        model_fields = cls.parse_fields(attributes)
        if attributes.get('__slots_optimization__', True):
            attributes['__slots__'] = cls.prepare_model_slots(model_fields)
        new_cls = type.__new__(cls, class_name, bases, attributes)
        new_cls.__fields__ = cls.bind_fields_to_model_cls(cls, model_fields)

    @staticmethod
    def parse_fields(attributes):
        return tuple(
            field.bind_name(name) for name, field in attributes.items()
            if isinstance(field, Field))

    @staticmethod
    def bind_fields_to_model_cls(new_cls, model_fields):
        return dict((field.name, field.bind_model_cls(new_cls))
                    for field in model_fields)

    @staticmethod
    def prepare_model_slots(model_fields):
        return tuple(filed.storage_name for field in model_fields)


class DomainModel(metaclass=DomainModelMetaClass):
    __fields__ = dict()
    __unique_key__ = tuple()

    def __init__(self, **kwargs):
        for name, field in self.__class__.__fields__.items():
            field.init_model(self, kwargs.get(name))

    def get(self, field_name):
        try:
            field = self.__class__.__fields__[field_name]
        except KeyError:
            raise AttributeError('{} does not exist'.format(field_name))
        else:
            return field.get_value(self)

    def get_data(self):
        return dict((name, field.get_builtin_type(self))
                    for name, field in self.__class__.__fields__.items())

    def set_data(self):
        for name, field in self.__class__.__fields__.items():
            field.init_model(self, data.get(name))


class WeldTypeStorage(WeldData):
    args = [{'abbreviation': String(), 'full_title': String()}]


class EqTypeStorage(WeldData):
    args = [{
        'abbreviation': String(),
        'full_title': String(),
    }]


class WeldTechnologyStorage(WeldData):
    args = [{
        'certificate': Int(),
        'cerification_date': Date(),
        'weld_type': WeldTypeStorage()
    }]


# class WeldEquipmentStorage(WeldData):
#     args = [{
#         'certificate': Int(),
#         'certification_date': Date(),
#         'weld_type': WeldTypeStorage(),
#         'equipment_type': EqTypeStorage()
#     }]

# class WeldMaterialTypeStorage(WeldData):
#     args = [{
#         'select': {
#             '01': 'Проволока сечения',
#             '02': 'Проволока порошковая',
#             '03': 'Газ защитный',
#             '04': 'Газ горючий',
#             '05': 'Флюс',
#             '06': 'Электрод плавящийся',
#             '07': 'Электрод неплавящийся'
#         }
#     }]

# class WeldMaterialStorage(WeldData):
#     args = [{
#         'certificate': Int(),
#         'certification_date': Date(),
#         'weld_type': WeldTypeStorage(),
#         'material_type': WeldMaterialTypeStorage()
#     }]


class WelderStorage(WeldData):
    args = [{
        'certificate': Int(),
        'career_start': Date(),
        'graduated_at': String(),
    }]


class WeldOrgStorage(WeldData):
    args = [{
        'short_name': String(),
        'full_name': String(),
        'available': Bool(),
        'staff_number': Int()
    }]


class Welder(DomainModel):
    def __init__(welder_name, uid, args):
        super().__init__()
        self.name = welder_name
        self.uid = uid
        self.storage = WelderStorage(title=welder_name, uid=uid, args=args)


class WeldOrg(DomainModel):
    def __init__(weld_org_title, uid, args):
        super().__init__()
        self.title = weld_org_title
        self.uid = uid
        self.storage = WeldOrgStorage(title=weld_org_title, uid=uid, args=args)


class ContextViewMetaclass(DetailView):
    def get_context_data(self, **kwargs):
        context = get_context_data(**kwargs)
        return context


class ContextView(ContextViewMetaclass):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WelderContextView(ContextView):
    model = Welder
    template_name = 'mainapp/weld_data_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['welders'] = Welder.objects.all()
        return context


class CreateViewMetaclass(CreateView):
    model = Welder
    template_name = 'mainapp/weld_data_form.html'
    success_url = reverse_lazy('news')
    fields = ('__all__')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'создание новых данных'
        print(context)
        return context


# class WeldOrgCreateView(ContextView):
#     def get_context_data(self, **kwargs):
#         context = super(WeldData, self).get_context_data(**kwargs)
#         context['title'] = 'создание нового профиля организации'

# class WeldOrgContextView(ContextView):
#     pass

# class WelderContextView(ContextView):
#     pass


class WeldListView(ListView):
    model = Welder
    paginate_by = 10
    template_name = 'mainapp/weld_data_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['welders'] = Welder.objects.all()
        return context
