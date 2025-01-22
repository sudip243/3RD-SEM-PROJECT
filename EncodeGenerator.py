import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://faceattendancerealtime-66579-default-rtdb.firebaseio.com/',
        'storageBucket': "faceattendancerealtime-66579.firebasestorage.app"
    })
except ValueError as e:
    print("Error:", e)


#importing the student images
folderPath = 'images'
PathList = os.listdir(folderPath)
#print(PathList)
imgList = []
studentIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path))) #mode folder er image gulo niy asa holo
 #   print(os.path.splitext(path)[0]) #first element take eai vabe naua jai
    studentIds.append(os.path.splitext(path)[0])#images er shudu name ta name extension chara

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


print(studentIds)

def findEncodings(imagesList):    #amra protiti images k loop e nilam o endoing korbo
    encodeList = []
    for img in imagesList:

        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #open cv bgr user kore face recognation libray rgb user kore
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList
print("encoding started......")
encodeListKnown = findEncodings(imgList) #this will find the image list and it will save it here
encodeListKnownWithIds = [encodeListKnown,studentIds] #encoding er por kon list ta kon idr seta dakhajai
#print(encodeListKnown)
print("encoding started")

file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("file saved")