from django.contrib.auth.models import AnonymousUser
from django_filters import rest_framework as filters

from recipes.models import Favourite, Recipe, Shopping_cart, User


class RecipeFilterSet(filters.FilterSet):
    BOOLEAN_CHOICES = (
        ('0', False),
        ('1', True),
    )

    is_favourited = filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='is_favourited',
        method='filter_is_favourited')
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='exact')

    def filter_is_favourited(self, queryset, name, value):
        user = self.request.user
        queryset = Recipe.objects.all()

        is_favourited = self.request.query_params.get('is_favourited')
        if is_favourited == '1':
            if type(user) is AnonymousUser:
                queryset = Recipe.objects.none()
            else:
                favourites = Favourite.objects.filter(user=user)
                queryset = Recipe.objects.filter(id__in=favourites.recipes)
        elif is_favourited == '0':
            if type(user) is not AnonymousUser:
                favourites = Favourite.objects.filter(user=user)
                queryset = Recipe.objects.exclude(id__in=favourites.recipes)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        queryset = Recipe.objects.all()

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart == '1':
            if type(user) is AnonymousUser:
                queryset = Recipe.objects.none()
            else:
                cart = Shopping_cart.objects.filter(user=user)
                queryset = Recipe.objects.filter(id__in=cart.recipes)
        elif is_in_shopping_cart == '0':
            if type(user) is not AnonymousUser:
                cart = Shopping_cart.objects.filter(user=user)
                queryset = Recipe.objects.exclude(id__in=cart.recipes)

        return queryset

    class Meta:
        model = Recipe
        fields = []
