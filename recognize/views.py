from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
import json
from recognize import utils
from recognize.models import Picture

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the recognize index.")

@csrf_exempt
@require_POST
def recognize(request: HttpRequest):
    try:
        user_id = request.POST.get('userId')
        picture = request.FILES.get('picture')
        if not user_id or not picture:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        image = Picture(user_id, picture)
        print("user reached here")
        result = utils.recognize(image)
        print("after result")
        photo_id = utils.save_photo(image)
    except ValueError as e:
        print(e)
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('recognize: ', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'message': 'Recognized', 'friends': result, 'photoId': str(photo_id)}), status=200)

@csrf_exempt
@require_GET
def photo(request: HttpRequest):
    try:
        photo_id = request.GET.get('id')
        photo = utils.get_photo(photo_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('photo: ', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(photo, content_type='image/jpeg')


@csrf_exempt
@require_POST
def send_photo(request: HttpRequest):
    try:
        body = json.loads(request.body)
        user_id = body.get('userId')
        photo_id = body.get('photoId')
        recipients = body.get('recipients')
        if not user_id or not photo_id or not recipients:
            return HttpResponse(json.dumps({'error': 'Missing required fields'}), status=400)
        
        result = utils.send_photo(user_id, photo_id, recipients)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('send_photo: ', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps({'message': 'Photo sent'}), status=200)

@csrf_exempt
def photos(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        photos = utils.get_photos(user_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('photos: ', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps(photos), status=200)

@csrf_exempt
@require_GET
def get_chat(request: HttpRequest):
    try:
        user_id = request.GET.get('userId')
        friend_id = request.GET.get('friendId')
        photos = utils.get_chat(user_id, friend_id)
    except ValueError as e:
        return HttpResponse(json.dumps({'error': str(e)}), status=400)
    except Exception as e:
        print('chat: ', e)
        return HttpResponse(json.dumps({'error': 'An error occurred'}), status=500)
    
    return HttpResponse(json.dumps(photos), status=200)