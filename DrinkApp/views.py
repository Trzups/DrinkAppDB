from django.shortcuts import render, redirect
import requests
from requests.exceptions import HTTPError
from django.http import HttpResponse
from django.contrib import messages


def index(request):
    if 'random_cocktail' in request.POST:
        random_drink = get_random_drink()
        try:
            random_drink.raise_for_status()
        except HTTPError as http_error:
            return HttpResponse(f'HTTP error occurred: {http_error}')
        drink = random_drink.json()
        drink_view = get_view_drink(drink)
        return render(request, 'index.html', drink_view)
    if request.method == 'POST':
        drink_name = request.POST['drink']
        drink = get_drink(drink_name)
        try:
            drink.raise_for_status()
        except HTTPError as http_error:
            return HttpResponse(f'HTTP error occurred: {http_error}')
        drink = drink.json()
        if drink['drinks'] is None:
            messages.error(request, 'Drink does not exist in the database')
            return redirect('index')
        drink_view = get_view_drink(drink)
        return render(request, 'index.html', drink_view)
    else:
        return render(request, 'index.html')


def get_drink(drink_name):
    drink = requests.get(f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={drink_name}')
    return drink


def get_view_drink(drink):
    drinks = view_drink(drink)
    context = {'drinks': drinks}
    return context


def get_random_drink():
    random_drink_request = requests.get('https://www.thecocktaildb.com/api/json/v1/1/random.php')
    return random_drink_request


def view_drink(drinks):
    drink_data = []
    for drink_detail in drinks['drinks']:
        drink_options = {
            'drink_name': drink_detail['strDrink'],
            'drink_instruction': drink_detail['strInstructions'],
            'drink_image': drink_detail['strDrinkThumb'],
            'drink_glass': drink_detail['strGlass'],
            'drink_category': drink_detail['strCategory'],
            'drink_ingredient': get_drink_ingredient(drink_detail)
        }
        drink_data.append(drink_options)
    return drink_data


def get_drink_ingredient(drink):
    drink_ingredient = {}
    max_ingredient = 16
    for item in range(1, max_ingredient, 1):
        if (drink[f'strIngredient{item}']) != None:
            drink_ingredient[(drink[f'strIngredient{item}'])] = (drink[f"strMeasure{item}"])
    return drink_ingredient
