from rest_framework import serializers
from .models import Task, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TaskCreateSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 'completed', 'user', 'categories']
        read_only_fields = ['user']

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        task = Task.objects.create(**validated_data)
        for category_data in categories_data:
            category, _ = Category.objects.get_or_create(**category_data)
            task.categories.add(category)
        return task

class TaskUpdateSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    title = serializers.CharField(required=False)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 'completed', 'user', 'categories']
        read_only_fields = ['user']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.completed = validated_data.get('completed', instance.completed)

        categories_data = validated_data.pop('categories', None)
        if categories_data is not None:
            instance.categories.clear()
            for category_data in categories_data:
                category, _ = Category.objects.get_or_create(**category_data)
                instance.categories.add(category)

        instance.save()
        return instance