import os
import pickle
import cvzone
import numpy as np
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://faceattendancerealtime-66579-default-rtdb.firebaseio.com/',
        'storageBucket': "faceattendancerealtime-66579.firebasestorage.app"
    })

except ValueError as e:
    print("Error:", e)
bucket = storage.bucket()

# Set the camera index to 0 (usually the default webcam)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

imgBackground = cv2.imread('Resources/background.png')

# importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModelist = []
for path in modePathList:
    imgModelist.append(cv2.imread(os.path.join(folderModePath, path)))  # mode folder er image gulo niy asa holo

# load the encoding file
print("loding Encoded file ......")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("encode file loaded")

if not cap.isOpened():
    print("Error: Could not open the webcam.")
    exit()

print("Press 'q' to exit.")

modeType = 0
counter = 0
id = -1
imgStudent = []
while True:
    ret, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # open cv bgr user kore face recognation libray rgb user kore

    faceCurFrame = face_recognition.face_locations(
        imgS)  # feeding the value to our face recogintaion system, faces in the current frame
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)  # 50.12 minute part ta dakhbo

    imgBackground[162:162 + 480, 55:55 + 640] = img  # background er vitore webcam ta set kora
    imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modeType]  # side er mode tha ana holo

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #       print(matches)
            #       print(faceDis)

            matchIndex = np.argmin(faceDis)
            # print(matchIndex)

            if matches[matchIndex]:  # green border chole asr jonno

                #  print("known face detected")
                #    print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "loading",(275,400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1) #delay hobe 1 sec
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # get the data
                studentInfo = db.reference(f'students/{id}').get()
                print(studentInfo)

                # get the image from the storage
                blob = bucket.get_blob(f'images/{id}.png')
                if blob is not None:
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                else:
                    print(f"Blob 'images/{id}.png' not found.")

                # update data of attendence
                datetimeObject = datetime.strptime(studentInfo['last_attendence_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'students/{id}')
                    studentInfo['total_attendence'] += 1  # attendence will incresing by 1
                    ref.child('total_attendence').set(studentInfo['total_attendence'])
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modeType]  # side er mode tha ana holo
            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendence']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (410 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modeType]

    else:
        modeType = 0
        counter = 0

    # Display the frame
    #    cv2.imshow('Logitech Webcam', frame) #640*480
    cv2.imshow("Face Attendance", imgBackground)  # 1280*720

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()
