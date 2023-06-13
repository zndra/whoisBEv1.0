
from django.http import JsonResponse
from .models import User

def get_users(request):
    users = User.objects.all().values('id', 'name')
    user_list = list(users)
    return JsonResponse(user_list, safe=False)
