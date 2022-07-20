from django_filters import rest_framework as filters

from recipes.models import Favourite, Recipe, ShoppingCart, User


class RecipeFilterSet(filters.FilterSet):
    BOOLEAN_CHOICES = (
        ('0', False),
        ('1', True),
    )

    is_favourited = filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        method='filter_is_favourited')
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        method='filter_is_in_shopping_cart')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='exact')

    def filter_is_favourited(self, queryset, name, value):
        user = self.request.user
        is_favourited = self.request.query_params.get('is_favourited')

        if user.is_authenticated:
            favourites = Favourite.objects.filter(
                user=user
            ).values_list('recipe')
        else:
            favourites = Favourite.objects.none()

        if is_favourited == '1':
            return Recipe.objects.filter(id__in=favourites)
        elif is_favourited == '0':
            return Recipe.objects.exclude(id__in=favourites)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if user.is_authenticated:
            shopping_cart = ShoppingCart.objects.filter(
                user=user
            ).values_list('recipe')
        else:
            shopping_cart = ShoppingCart.objects.none()

        if is_in_shopping_cart == '1':
            return Recipe.objects.filter(id__in=shopping_cart)
        elif is_in_shopping_cart == '0':
            return Recipe.objects.exclude(id__in=shopping_cart)

    class Meta:
        model = Recipe
        fields = []
