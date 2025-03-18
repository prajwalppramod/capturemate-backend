from user.models import User, ProfilePicture, FaceEncoding, Friend
from database import StorageConnection

connection = StorageConnection()

def get_user_by_id(user_id):
    user = connection.find_document_by_id('users', user_id)
    if not user:
        print('User not found', user_id)
        raise ValueError('User not found')
    return User(user=user)

def get_user(email = None, username = None):
    query = {}
    if email:
        query['email'] = email
    if username:
        query['username'] = username
    user = connection.find_document('users', query)
    return User(user=user) if user else None

def does_user_exist(email = None, username = None):
    return get_user(email, username) is not None

def is_username_taken(username):
    return does_user_exist(username=username)

def is_email_taken(email):
    return does_user_exist(email=email)

def register_user(email, username, password):
    if is_email_taken(email):
        raise ValueError('Email already taken')
    if is_username_taken(username):
        raise ValueError('Username already taken')
    
    user = User(username, email, password)
    
    user_result = connection.insert_document('users', user.to_db_json())
    return user_result

def login_user(username, password):
    user = get_user(username=username)
    if not user:
        raise ValueError('User not found')
    if not user.check_password(password):
        raise ValueError('Incorrect password')
    return user

def update_user(user_id, update):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError('User not found')
    user_result = connection.update_document_by_id('users', user_id, update)
    return user_result

def get_profile_picture(user_id):
    try:
        picture_bytes = connection.find_document('profile_pictures', {'userId': user_id})['profile_picture']
        profile_picture = ProfilePicture.from_bytes(picture_bytes)
        return profile_picture
    except:
        try:
            img = open('user/media/default-profile-picture.png', 'rb')
            profile_picture = ProfilePicture.from_bytes(img.read())
            return profile_picture
        except Exception as e:
            print(e)
            return None

def update_profile_picture(user_id, profile_picture_file):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError('User not found')
    profile_picture = ProfilePicture(user_id, profile_picture_file)
    insert_picture_result = connection.update_document('profile_pictures', {'userId': user_id}, {'$set': {'profile_picture': profile_picture.to_bytes()}}, upsert=True)
    return insert_picture_result

def onboard(user_id, onboarding_picture_file):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError('User not found')
    
    face_encoding = FaceEncoding(user_id, onboarding_picture_file)
    insert_face_encoding_result = connection.update_document('face_encodings', {'userId': user_id}, {'$set': {'face_encoding': face_encoding.face_encoding.tolist()}}, upsert=True)
    update_result = update_user(user_id, {'$set': {'onboarded': True}})
    return insert_face_encoding_result

def find_users(query):
    users = connection.find_documents('users', {
        "username": {"$regex": f'.*{query}.*'}
    })
    return [User(user=user) for user in users]

def add_or_remove_friend(user_id, friend_id):
    if not get_user_by_id(user_id):
        raise ValueError('User not found')
    if not get_user_by_id(friend_id):
        raise ValueError('Friend User not found')
    friends = get_friends(user_id, id_only=True)

    if friend_id in friends:
        remove_friend_result = connection.update_document('friends', {'userId': user_id}, {"$pull" : {"friends": { 'id': friend_id }}})
        return remove_friend_result

    add_friend_result = connection.update_document('friends', {'userId': user_id}, {"$addToSet" : {"friends": { 'id': friend_id, 'approved': False }}}, upsert=True)
    return add_friend_result

def get_friend(friend_id, approved = None):
    return Friend(get_user_by_id(friend_id), approved=approved)

def get_friends(user_id, id_only = False):
    if not get_user_by_id(user_id):
        raise ValueError('User not found')

    friends_result = connection.find_document('friends', {'userId': user_id})
    if friends_result is None:
        return []
    if id_only:
        return [friend.get('id') for friend in friends_result['friends']]
    return [get_friend(friend.get('id'), friend.get('approved')).to_client_json() for friend in friends_result['friends']]

def get_pending_invites(user_id):
    try:
        if not get_user_by_id(user_id):
            raise ValueError('User not found')
        friend_requests_result = connection.find_documents('friends', {'friends': {'id': user_id, 'approved': False}})
        if friend_requests_result is None:
            return []
        friends = []
        while friend_requests_result.alive:
            friend = friend_requests_result.next()
            friends.append(get_friend(friend.get('userId'), False).to_client_json())
        return friends
    except Exception as e:
        print(e)
        return []

def accept_or_reject_invite(user_id, friend_id, status):
    if status == 'ACCEPTED':
        accept_friend_result = connection.update_document('friends', {'userId': friend_id, 'friends': {'id': user_id, 'approved': False}}, {"$set" : {"friends.$": {'id': user_id, 'approved': True}}})
        add_friend_result = connection.update_document('friends', {'userId': user_id}, {"$addToSet" : {"friends": {'id': friend_id, 'approved': True}}}, upsert=True)
        return accept_friend_result and add_friend_result
    elif status == 'REJECTED':
        reject_friend_result = connection.update_document('friends', {'userId': friend_id}, {"$pull" : {"friends": { 'id': user_id, 'approved': False}}})
        return reject_friend_result
    else:
        raise ValueError('Invalid status')

def reject_friend_request(user_id, friend_id):
    if not get_user_by_id(user_id):
        raise ValueError('User not found')
    if not get_user_by_id(friend_id):
        raise ValueError('Friend User not found')
    reject_friend_result = connection.update_document('friends', {'userId': friend_id}, {"$pull" : {"friends": { 'id': user_id }}})
    return reject_friend_result

def accept_friend_request(user_id, friend_id):
    if not get_user_by_id(user_id):
        raise ValueError('User not found')
    if not get_user_by_id(friend_id):
        raise ValueError('Friend User not found')
    accept_friend_result = connection.update_document('friends', {'userId': friend_id, 'friends': {'id': user_id}}, {"$set" : {"friends": {'id': user_id, 'approved': True}}})
    add_friend_result = connection.update_document('friends', {'userId': user_id}, {"$addToSet" : {"friends": {'id': friend_id, 'approved': True}}})
    return accept_friend_result and add_friend_result