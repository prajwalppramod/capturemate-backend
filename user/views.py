from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from user import db
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the user index.")

@csrf_exempt
@require_POST
def register(request: HttpRequest):
    try:
        body = json.loads(request.body)
        email = body.get('email')
        username = body.get('username')
        password = body.get('password')
        if not email or not username or not password:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        result = db.register_user(email, username, password)
        user = db.get_user_by_id(result.inserted_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('register: ', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'message': 'User registered', 'user': user.to_client_json()}), status=201)


@csrf_exempt
@require_POST
def login(request: HttpRequest):
    try:
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        if not username or not password:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        
        user = db.login_user(username, password)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'message': 'User logged in', 'user': user.to_client_json()}), status=200)


@csrf_exempt
def handle_profile_picture(request: HttpRequest):
    if request.method == 'POST':
        return update_profile_picture(request)
    elif request.method == 'GET':
        return get_profile_picture(request)
    else:
        return HttpResponse(json.dumps({'error': 'Method not allowed'}), status=405)

def get_profile_picture(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        if not user_id:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        profile_picture = db.get_profile_picture(user_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('profile picture error:', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    if not profile_picture:
        return HttpResponse('', status=404)
    return HttpResponse(content=profile_picture, status=200, content_type='image/jpeg')

def update_profile_picture(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        profile_picture = request.FILES.get('profilePicture')
        if not user_id or not profile_picture:
            print(user_id, profile_picture)
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        # print(profile_picture)
        db.update_profile_picture(user_id, profile_picture)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'message': 'Profile picture updated'}), status=200)


@csrf_exempt
@require_POST
def onboarding(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        onboarding_picture = request.FILES.get('picture')
        if not user_id or not onboarding_picture:
            print(user_id, onboarding_picture)
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        # print(onboarding_picture)
        db.onboard(user_id, onboarding_picture)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'message': 'Profile picture updated'}), status=200)

@csrf_exempt
def find_people(request: HttpRequest):
    try:
        query = request.GET.get('query')
        user_id = request.GET.get('userId')
        if not query or not user_id:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        users = db.find_users(query)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'users': [user.to_client_json() for user in users if user.user_id != user_id]}), status=200)

@csrf_exempt
def friends(request: HttpRequest):
    try:
        print("hello")
        if request.method == 'POST':
            return add_or_remove_friend(request)
        elif request.method == 'GET':
            return get_friends(request)
        else:
            return HttpResponse(json.dumps({'error': 'Unsupported method'}), status = 405)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occured'}), status=500)

def add_or_remove_friend(request: HttpRequest):
    try:
        body = json.loads(request.body)
        user_id, friend_id = body.get('userId'), body.get('friendId')
        result = db.add_or_remove_friend(user_id, friend_id)
    except ValueError as e:
        print(e)
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'An error occured'}), status=500)

    return HttpResponse(json.dumps({'message': 'success'} if result else {'error': 'add friend failed'}), status = 200 if result else 400)

def get_friends(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        if not user_id:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        friends = db.get_friends(user_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('get friends error:', e)
        return HttpResponse(json.dumps({'error': 'An error occured'}), status=500)

    return HttpResponse(json.dumps(friends), status = 200)

@csrf_exempt
def friend_invites(request: HttpRequest):
    try:
        if request.method == 'POST':
            return accept_or_reject_invite(request)
        elif request.method == 'GET':
            return get_pending_invites(request)
        else:
            return HttpResponse(json.dumps({'error': 'Unsupported method'}), status = 405)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occured'}), status=500)

def accept_or_reject_invite(request: HttpRequest):
    try:
        body = json.loads(request.body)
        user_id, friend_id, status = body.get('userId'), body.get('friendId'), body.get('status')
        result = db.accept_or_reject_invite(user_id, friend_id, status)
    except ValueError as e:
        print(e)
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        return HttpResponse(json.dumps({'error': 'An error occured'}), status=500)

    return HttpResponse(json.dumps({'message': 'success'} if result else {'error': 'add friend failed'}), status = 200 if result else 400)

def get_pending_invites(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        if not user_id:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        pending_invites = db.get_pending_invites(user_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'error': 'An error occured'}), status=500)

    return HttpResponse(json.dumps(pending_invites), status = 200)