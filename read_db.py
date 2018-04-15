from pymongo import MongoClient


class Colour:
    Green, Red, White, Yellow = '\033[92m', '\033[91m', '\033[0m', '\033[93m'

print(Colour.Yellow + """
╔═╗╔═╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
DATABASE READER THING...
╚═╝╚═╝╚═╝ ╩ ╚╩╝╩ ╩ ╩ ╚═╝ v1.0
""")
print(Colour.White + 'Press Ctrl + C to exit\n')

try:
    client = MongoClient('localhost')
    db = client.putln2
    df = db.friends
except:
    print(Colour.Red + "Could not connect to MongoDB")
    sys.exit()


count = 0
for x in df.find():
    user_id = x['id']
    username = x['username']
    location = x['user_location']
    description = x['description']
    try:
        if 'London' in location or 'wood' in description:
            count += 1
            print(Colour.White + user_id, username, location + '\n' + description + '\n')
    except Exception:
        pass

print(Colour.White + 'Found ' + Colour.Green + str(count) + Colour.White + ' users')
