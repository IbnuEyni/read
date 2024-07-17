from django.urls import path, include
from . import views

from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers


router = routers.DefaultRouter()

router.register("books", views.BooksViewSet)
router.register("categories", views.CategoryViewSet)
router.register("carts", views.CartViewSet)
router.register("n_profiles", views.ProfileViewSet)
router.register("orders", views.OrderViewSet, basename="order-list")

# Create a nested router
book_router = routers.NestedDefaultRouter(router, "books", lookup="book")
book_router.register("reviews", views.ReviewViewSet, basename="book-reviews")

cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")

# Define the URL patterns
urlpatterns = [
    path("", include(router.urls)),
    path("", include(book_router.urls)),
    path("",include(cart_router.urls)),
#     path("books", views.ApiBooks.as_view()),
#     path("books/<str:pk>", views.ApiBook.as_view()),
#     path("categories", views.APICategories.as_view()),
#     path("categories/<str:pk>", views.APICategory.as_view())
]

