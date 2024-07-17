from rest_framework import serializers
from core.models import *
from django.db import transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "title", "slug"]

# class BookImageSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = BookImage
#         fields = ["id", "book", "image"]

class BookSerializer(serializers.ModelSerializer):
    # images = BookImageSerializer(many=True, read_only=True)
    # uploaded_images = serializers.ListField(
    #     child = serializers.ImageField(max_length = 1000000, allow_empty_file = False, use_url = False),
    #     write_only = True
    # )
    class Meta:
        model = Book
        fields = [ "id", "title", "description", "category", "slug", "status", "owner", "purchase_price", "rental_price", "images"]

    category = CategorySerializer

    def create(self, validated_data):
        uploaded_images = validated_data.pop()
        book= Book.objects.create(**validated_data)
        for image in uploaded_images:
            newbook_image = BookImage.objects.create(book = book, image = image)
        return book

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model: Review
        fields = ["id", "date_created", "name", "description"]

    def create(self, validated_data):
        book_id = self.context["book_id"]
        return Review.objects.create(book_id = book_id,  **validated_data)
    class Meta:
        model = Review
        fields = ["id", "date_created", "name", "description"]


class SimpleBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id","title", "purchase_price"]

class CartItemSerializer(serializers.ModelSerializer):
    book = SimpleBookSerializer(many=False)
    sub_total = serializers.SerializerMethodField( method_name="total")
    class Meta:
        model= Cartitems
        fields = ["id", "cart", "book", "quantity", "sub_total"]
        
    
    def total(self, cartitem:Cartitems):
        return cartitem.quantity * cartitem.book.purchase_price


class AddCartItemSerializer(serializers.ModelSerializer):
    book_id = serializers.UUIDField()
    
    def validate_book_id(self, value):
        if not Book.objects.filter(pk=value).exists():
            raise serializers.ValidationError("There is no book associated with the given ID")
        
        return value
    
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        book_id = self.validated_data["book_id"] 
        quantity = self.validated_data["quantity"] 
        
        try:
            cartitem = Cartitems.objects.get(book_id=book_id, cart_id=cart_id)
            cartitem.quantity += quantity
            cartitem.save()
            
            self.instance = cartitem
            
        
        except:
            
            self.instance = Cartitems.objects.create(cart_id=cart_id, **self.validated_data)
            
        return self.instance
         

    class Meta:
        model = Cartitems
        fields = ["id", "book_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Cartitems
        fields = ["quantity"]



class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField(method_name='main_total')
    
    class Meta:
        model = Cart
        fields = ["id", "items", "grand_total"]
        
    
    
    def main_total(self, cart: Cart):
        items = cart.items.all()
        total = sum([item.quantity * item.book.purchase_price for item in items])
        return total
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", 'bio', "picture"]


class OrderItemSerializer(serializers.ModelSerializer):
    book = SimpleBookSerializer()
    class Meta:
        model = OrderItem 
        fields = ["id", "book", "quantity"]
        


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order 
        fields = ['id', "placed_at", "pending_status", "owner", "items"]
        

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This cart_id is invalid")
        
        elif not Cartitems.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError("Sorry your cart is empty")
        
        return cart_id
    
    
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            order = Order.objects.create(owner_id = user_id)
            cartitems = Cartitems.objects.filter(cart_id=cart_id)
            orderitems = [
                OrderItem(order=order, 
                    book=item.book, 
                    quantity=item.quantity
                    )
            for item in cartitems
            ]
            OrderItem.objects.bulk_create(orderitems)
            # Cart.objects.filter(id=cart_id).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order 
        fields = ["pending_status"]