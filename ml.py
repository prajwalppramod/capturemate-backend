import numpy as np
import io
import PIL.Image
import face_recognition
from django.core.files.uploadedfile import UploadedFile

def open_image(image_file: UploadedFile):
    image_file = image_file.open()
    in_memory_image_file = io.BytesIO(image_file.read())
    im = PIL.Image.open(in_memory_image_file)
    im = im.convert('RGB')
    return np.array(im)

def get_face_encodings(image_file: UploadedFile):
    image = open_image(image_file)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings

def get_face_encoding(image_file: UploadedFile):
    return get_face_encodings(image_file)[0]

def recognize_faces(image_file: UploadedFile, known_face_encodings, known_face_ids):
    recognized_faces = set()
    unknown_image = open_image(image_file)

    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            recognized_faces.add(known_face_ids[best_match_index])
    
    return list(recognized_faces)


# def add_face_encoding(file_name, person_name, known_face_encodings, known_face_names):

#     person_image = face_recognition.load_image_file(file_name)
#     person_face_encoding = face_recognition.face_encodings(person_image)[0]
#     known_face_encodings.append(person_face_encoding)
#     known_face_names.append(person_name)
#     print('Learned encoding for', person_name,'.')