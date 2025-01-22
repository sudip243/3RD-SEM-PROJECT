import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://faceattendancerealtime-66579-default-rtdb.firebaseio.com/'
    })
except ValueError as e:
    print("Error:", e)

ref = db.reference('students')

data = {
    "321001":
        {
            "name": "MS Dhoni",
            "major": "keeper",
            "starting_year": 2008,
            "total_attendence": 10,
            "standing": "6",
            "year": 4,
            "last_attendence_time": "2025-12-11 00:54:34"
        },
    "321002":
        {
            "name": "Rohit Sharma",
            "major": "opener",
            "starting_year": 2008,
            "total_attendence": 10,
            "standing": "6",
            "year": 4,
            "last_attendence_time": "2024-12-11 00:54:34"
        },
    "321003":
        {
            "name": "Sachin Sir",
            "major": "Bats man",
            "starting_year": 2008,
            "total_attendence": 10,
            "standing": "6",
            "year": 4,
            "last_attendence_time": "2023-12-11 00:54:34"
        },
    "321004":
        {
            "name": "Virat Kholi",
            "major": "cricket king",
            "starting_year": 2008,
            "total_attendence": 10,
            "standing": "6",
            "year": 4,
            "last_attendence_time": "2022-12-11 00:54:34"
        },
    "321005":
        {
            "name": "Sudipto",
            "major": "allrounder",
            "starting_year": 2008,
            "total_attendence": 10,
            "standing": "6",
            "year": 4,
            "last_attendence_time": "2024-10-10 00:54:34"
        }

}
for key,value in data.items():
    ref.child(key).set(value)