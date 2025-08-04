from django.shortcuts import render

# Create your views here.

def recipes_view(request):
    return render(request, 'recipes/recipes.html')