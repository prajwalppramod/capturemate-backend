from django.contrib.auth.hashers import make_password, check_password
from django.core.files.uploadedfile import UploadedFile
import io
import ml
# Create your models here.

class User:
    def __init__(self, username = None, email = None, password = None, user = None, user_id = None):
        if user:
            self.user_id = str(user['_id']) if '_id' in user else None
            self.username = user['username']
            self.email = user['email']
            self.password = user['password']
            self.onboarded = user.get('onboarded', False)
        else:
            self.user_id = user_id
            self.username = username
            self.email = email
            self.password = make_password(password) if password else None
            self.onboarded = False
    
    def __str__(self) -> str:
        return f'User: {self.username}'

    def to_db_json(self):
        json = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'onboarded': self.onboarded
        }
        if self.user_id:
            json['_id'] = self.user_id
        return json
    
    def to_client_json(self):
        json = {
            'username': self.username,
            'email': self.email,
            'onboarded': self.onboarded
        }
        if self.user_id:
            json['userId'] = self.user_id
        return json

    def check_password(self, password):
        return check_password(password, self.password)

class Friend(User):
    def __init__(self, user:User=None, approved=None, user_id=None, username=None, email=None):
        if user:
            super().__init__(user_id=user.user_id, username=user.username, email=user.email)
            self.approved = approved
        else:
            super().__init__(username, email, None)
            self.user_id = user_id
            self.approved = approved

    def to_client_json(self):
        return {
            'userId': self.user_id,
            'username': self.username,
            'email': self.email,
            'approved': self.approved
        }
    
class ProfilePicture:
    def __init__(self, user_id: str, profile_picture: UploadedFile):
        self.user_id = user_id
        self.profile_picture = profile_picture
        
    def __str__(self) -> str:
        return f'Profile Picture for User: {self.user_id}'
    
    def to_bytes(self):
        picture = self.profile_picture.open()
        return io.BytesIO(picture.read()).getvalue()
    
    @staticmethod
    def from_bytes(bytes):
        return io.BytesIO(bytes)

class FaceEncoding:
    def __init__(self, user_id: str, onboarding_picture: UploadedFile):
        self.user_id = user_id
        self.face_encoding = ml.get_face_encoding(onboarding_picture)
    
    def __str__(self) -> str:
        return f'Face Encoding for User: {self.user_id}'
    
    def to_json(self):
        return {
            'user_id': self.user_id,
            'face_encoding': self.face_encoding.tolist()
        }