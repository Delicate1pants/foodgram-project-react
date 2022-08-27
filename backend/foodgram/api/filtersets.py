from django_filters import rest_framework as filters

from recipes.models import Favourite, Recipe, ShoppingCart, User, Tag


class RecipeFilterSet(filters.FilterSet):
    BOOLEAN_CHOICES = (
        ('0', False),
        ('1', True),
    )

    is_favorited = filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        method='filter_is_favorited')
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        method='filter_is_in_shopping_cart')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')

        if user.is_authenticated:
            favorites = Favourite.objects.filter(
                user=user
            ).values_list('recipe')
        else:
            favorites = Favourite.objects.none()

        if is_favorited == '1':
            return Recipe.objects.filter(id__in=favorites)
        elif is_favorited == '0':
            return Recipe.objects.exclude(id__in=favorites)

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
