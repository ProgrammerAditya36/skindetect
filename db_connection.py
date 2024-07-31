import pymongo
url = "mongodb+srv://admin:test123@cluster0.dahrvb8.mongodb.net/"
client = pymongo.MongoClient(url)
db = client['skindetect']
userCollection = db['users']
def addUser(formData):
    user = {
        "first_name": formData.get('first_name'),
        "last_name": formData.get('last_name'),
        "email": formData.get('email'),
        "phone": formData.get('phone'),
        "dob": formData.get('dob'),
        "gender": formData.get('gender'),
        "phone": formData.get('phone'),
        "address": formData.get('address'),
        "city": formData.get('city'),
        "state": formData.get('state'),
        "zip_code": formData.get('zip_code'),
        "any_previous_diseases": formData.get('any_previous_diseases'),

    }
    userCollection.insert_one(user)
    print("User added to MongoDB")
    return user
