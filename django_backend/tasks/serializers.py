from rest_framework import serializers
from .models import Task, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TaskSerializer(serializers.ModelSerializer):
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