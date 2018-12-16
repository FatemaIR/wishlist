from django.shortcuts import render, redirect
from django.http import JsonResponse
from items.models import Item, FavoriteItem
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q

# Create your views here.
def item_list(request):
    items = Item.objects.all()
    items_fav = []
    if request.user.is_authenticated:
        my_favs = FavoriteItem.objects.filter(user=request.user)
        items_fav = [fav.item for fav in my_favs]

    query = request.GET.get("q")
    if query:
        items = items.filter(name__contains=query)

    context = {
        "items": items,
        "items_fav": items_fav,
    }
    return render(request, 'item_list.html', context)

def item_detail(request, item_id):
    context = {
        "item": Item.objects.get(id=item_id)
    }
    return render(request, 'item_detail.html', context)

#to favorite the item
def item_favorite(request, item_id):
    item_obj = Item.objects.get(id=item_id)
    fav_obj, created = FavoriteItem.objects.get_or_create(item=item_obj, user=request.user)

    if created:
        action = "fav"
    else:
        action = "unfav"
        fav_obj.delete()
    response = {
        "action": action,
    }
    return JsonResponse(response)

#save in wishlist
def favorite_items(request):
    if request.user.is_anonymous:
        return redirect('signin')

    items = Item.objects.all()
    my_favs= FavoriteItem.objects.filter(user=request.user)
    items_fav = [fav.item for fav in my_favs]

    query = request.GET.get("q")
    if query:
        my_favs = FavoriteItem.objects.filter(item__name__contains=query)
        items_fav = [fav.item for fav in my_favs]

    context = {
        "items_fav": items_fav,
        "my_favs": my_favs,
    }
    
    return render(request, 'favorite.html', context)

def user_register(request):
    register_form = UserRegisterForm()
    if request.method == "POST":
        register_form = UserRegisterForm(request.POST)
        if register_form.is_valid():
            user = register_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            login(request, user)
            return redirect('item-list')
    context = {
        "register_form": register_form
    }
    return render(request, 'user_register.html', context)

def user_login(request):
    login_form = UserLoginForm()
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect('item-list')
    context = {
        "login_form": login_form
    }
    return render(request, 'user_login.html', context)

def user_logout(request):
    logout(request)

    return redirect('item-list')