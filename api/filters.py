from django_filters.rest_framework import FilterSet
from core.models import Book, Review


class BookFilter(FilterSet):
    class Meta:
        model =  Book
        fields = {
            'category_id': ['exact'],
            'purchase_price': ['gt', 'lt']
        }
    def create(self, validated_data):
        product_id = self.context["product_id"]
        return Review.objects.create(product_id = product_id,  **validated_data)