from recognize.models import Picture
import ml
from database import StorageConnection
from user.db import get_friends, get_friend

from pymongo.results import InsertOneResult
from bson.objectid import ObjectId

connection = StorageConnection()

def get_saved_face_encoding(user_id: str):
    return connection.find_document('face_encodings', {'userId': user_id})['face_encoding']

def get_friends_encodings_list(user_id: str):
    friend_ids = get_friends(user_id, id_only=True)
    return ([get_saved_face_encoding(id) for id in friend_ids], friend_ids)

def get_people_in_image(image: Picture):
    friend_encodings, friend_ids = get_friends_encodings_list(image.user_id)
    return ml.recognize_faces(image.picture, friend_encodings, friend_ids)

def recognize(image: Picture):
    friend_ids = get_people_in_image(image)
    print("hello",friend_ids)

    return [get_friend(friend_id).to_client_json() for friend_id in friend_ids]

def save_photo(image: Picture):
    result: InsertOneResult = connection.insert_document('photos', {'photo': image.to_bytes()})
    photo_id: ObjectId = result.inserted_id
    add_photo_to_list(image, str(photo_id))
    return photo_id

def add_photo_to_list(image: Picture, photo_id: str):
    result = connection.update_document('user_photos', {'userId': image.user_id}, {'$addToSet': {'photos': {"id": photo_id, "name": image.picture.name}}}, upsert=True)
    return result

def get_photos(user_id: str):
    photos = connection.find_document('user_photos', {'userId': user_id})
    if not photos:
        return []
    return photos['photos']

def get_photo(photo_id: str):
    return connection.find_document_by_id('photos', photo_id)['photo']

def send_photo(user_id, photo_id, recipients):
    for recipient in recipients:
        result = connection.insert_document('received_photos', {'userId': recipient, 'photoId': photo_id, 'sender': user_id})
    return result

def get_chat(user_id, friend_id):
    photos = connection.find_documents('received_photos', {'userId': {'$in': [user_id, friend_id]}, 'sender': {'$in': [user_id, friend_id]}})


    chat = []
    for photo in photos:
        chat.append({
            'photoId': photo['photoId'],
            'sent': photo['sender'] == user_id
        })
    return chat