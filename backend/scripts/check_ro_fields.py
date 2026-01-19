import inspect
from django.conf import settings
from rest_framework import serializers

def find_ro_fields(serializer_cls):
    try:
        ser = serializer_cls()
    except Exception:
        # require context or queryset, skip
        return []
    ro = []
    try:
        for name, field in ser.fields.items():
            if isinstance(field, serializers.ReadOnlyField):
                ro.append(name)
    except Exception:
        return []
    return ro

def main():
    print("Scanning serializers for ReadOnlyField occurrences...")
    modules = []
    try:
        from inventario import serializers as inv_ser
        modules.append(inv_ser)
    except Exception as e:
        print("inventario serializers import error:", e)
    try:
        from compras import serializers as com_ser
        modules.append(com_ser)
    except Exception as e:
        print("compras serializers import error:", e)
    try:
        from geography import serializers as geo_ser
        modules.append(geo_ser)
    except Exception as e:
        print("geography serializers import error:", e)
    try:
        from catalogo import serializers as cat_ser
        modules.append(cat_ser)
    except Exception as e:
        print("catalogo serializers import error:", e)
    try:
        from notificaciones import serializers as noti_ser
        modules.append(noti_ser)
    except Exception as e:
        print("notificaciones serializers import error:", e)
    try:
        from auditoria import views as aud_views
        # collect serializer classes defined in views
        for name, obj in inspect.getmembers(aud_views):
            if inspect.isclass(obj) and issubclass(obj, serializers.Serializer):
                modules.append(obj)
    except Exception as e:
        print("auditoria views import error:", e)

    for mod in modules:
        if inspect.ismodule(mod):
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj) and issubclass(obj, serializers.BaseSerializer):
                    ro = find_ro_fields(obj)
                    if ro:
                        print(f"{obj.__module__}.{obj.__name__}: ReadOnlyField -> {ro}")
        elif inspect.isclass(mod) and issubclass(mod, serializers.BaseSerializer):
            ro = find_ro_fields(mod)
            if ro:
                print(f"{mod.__module__}.{mod.__name__}: ReadOnlyField -> {ro}")

if __name__ == '__main__':
    main()