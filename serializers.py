from rest_framework import serializers
import neomodel


class GenericNeomodelSerializer(serializers.Serializer):
    serializer_field_mapping = {
        neomodel.UniqueIdProperty: serializers.UUIDField,
        neomodel.StringProperty: serializers.CharField,
        neomodel.IntegerProperty: serializers.IntegerField,
        neomodel.DateTimeProperty: serializers.DateTimeField,
    }

    # 定义可能的属性列表
    field_option_attrs = [
        "max_length",
        "required",
        "min_value",
        "max_value",
        "min_length",
        "blank",
        "default",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 判空
        assert hasattr(
            self, "Meta"
        ), 'Class {serializer_class} missing "Meta" attribute'.format(
            serializer_class=self.__class__.__name__
        )
        assert hasattr(
            self.Meta, "model"
        ), 'Class {serializer_class} missing "Meta.model" attribute'.format(
            serializer_class=self.__class__.__name__
        )

        read_only_fields = getattr(self.Meta, "read_only_fields", None)
        if read_only_fields is not None:
            if not isinstance(read_only_fields, (list, tuple)):
                raise TypeError(
                    "The `read_only_fields` option must be a list or tuple. "
                    "Got %s." % type(read_only_fields).__name__
                )

        # 获取字段
        field_set = getattr(self.Meta.model, "__all_properties__")
        if self.Meta.fields != serializers.ALL_FIELDS:
            field_set = tuple(item for item in field_set if item[0] in self.Meta.fields)

        for field_name, field in field_set:
            # 获取字段的类型
            field_type = type(field)

            # 检查字段类型是否在 serializer_field_mapping 中
            if field_type in self.serializer_field_mapping:
                # 根据字段类型获取对应的序列化器字段类
                serializer_field_class = self.serializer_field_mapping[field_type]

                # 取属性
                field_kwargs = {}
                if read_only_fields is not None and field_name in read_only_fields:
                    field_kwargs["read_only"] = True

                for attr in self.field_option_attrs:
                    # 这个if为了保护uuid不被加上default属性
                    if type(field).__name__ == "UniqueIdProperty" and attr == "default":
                        continue

                    value = getattr(field, attr, None)
                    if value is not None:
                        field_kwargs[attr] = value

                # 创建序列化器字段实例并赋值给字段
                if not field_name in self.fields:
                    self.fields[field_name] = serializer_field_class(**field_kwargs)

    def create(self, validated_data):
        return self.Meta.model(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
