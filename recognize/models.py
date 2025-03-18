from django.db import models
from django.core.files.uploadedfile import UploadedFile
import io
# Create your models here.
class Picture:
    def __init__(self, user_id, picture: UploadedFile):
        self.user_id = user_id
        self.picture = picture

    def to_bytes(self):
        picture = self.picture.open()
        return io.BytesIO(picture.read()).getvalue()
    
    @staticmethod
    def from_bytes(bytes):
        return io.BytesIO(bytes)

    def to_db_json(self):
        json = {
            'user_id': self.user_id,
            'picture': self.to_bytes(),
        }
        return json