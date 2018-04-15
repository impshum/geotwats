import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from pymongo import MongoClient
import sys
import time
import json
import smtplib
from halo import Halo


send_dm = 1 # Send Twitter DM to victims
send_mail = 1 # Send email alerts
box_boundary = [-0.17, 51.52, 0.11, 51.62] # Box boundary http://bboxfinder.com/
dm_message = "Hi! Wanna buy a coconut?" # Message to send to user on Twitter
email_msg = "looks like they're gonna be fun." # Email alert message (@USER msg)

email_server = 'smtp.gmail.com' # Email server
email_port = 465 # Email server port
email_account = 'XXXX' # Email address
email_password = 'XXXX' # Email password
send_to = 'XXXX' # Email address to send alert to

consumer_key = 'XXXX' # Twitter keys
consumer_secret = 'XXXX' # Twatter keys
access_key = 'XXXX-XXXX' # Twerper keys
access_secret = 'XXXX' # Twitter keys

finds = ['XXXX', 'XXXX', 'XXXX', 'XXXX', 'XXXX', 'XXXX'] # Strings to search for in stream


class Colour:
    Green, Red, White, Yellow = '\033[92m', '\033[91m', '\033[0m', '\033[93m'


print(Colour.Yellow + """
╔═╗╔═╗╔═╗╔╦╗╦ ╦╔═╗╔╦╗╔═╗
║ ╦║╣ ║ ║ ║ ║║║╠═╣ ║ ╚═╗
╚═╝╚═╝╚═╝ ╩ ╚╩╝╩ ╩ ╩ ╚═╝ v1.0
""")
print(Colour.White + 'Press Ctrl + C to exit\n')

try:
    client = MongoClient('localhost')
    db = client.geotwats
    du = db.users
except:
    print(Colour.Red + "Could not connect to MongoDB")
    sys.exit()


def mailer(send_body):
    try:
        message = 'Subject: {}\n\n{}'.format('GeoTwat', send_body)
        server = smtplib.SMTP_SSL(email_server, email_port)
        server.ehlo()
        server.login(email_account, email_password)
        server.sendmail(email_account, send_to, message)
        server.close()
        msg = Colour.Green + 'Email sent!'
        spinner.text = msg
    except Exception as e:
        if not 'ascii' in str(e):
            msg = Colour.Red + str(e)
            spinner.text = msg
            pass # as it's a right twat!


def check_string(string, substring_list):
    for substring in substring_list:
        if substring in string:
            return True
    return False


def check_user(user):
    get = du.find({'username': user}).count()
    if get:
        return True
    else:
        return False


def update_tags(ref, new_tag):
    du.update({'username': ref}, {'$push': {'hashtags': new_tag}})


def check_tags(user, tag):
    items = []
    for item in du.distinct('hashtags', {'username': user}):
        items.append(item)
    if not check_string(tag, items):
        msg = Colour.White + 'New hashtag found: ' + Colour.Green + tag
        spinner.text = msg
        update_tags(user, tag)


class listener(StreamListener):
    def on_data(self, data):
        all_data = json.loads(data)
        if 'text' in all_data:
            user_id = all_data["user"]["id"]
            followers = all_data["user"]["followers_count"]
            friends = all_data["user"]["friends_count"]
            statuses_count = all_data["user"]["statuses_count"]
            description = all_data["user"]["description"]
            twerp = all_data["text"]
            created_at = all_data["created_at"]
            username = all_data["user"]["screen_name"]
            name = all_data["user"]["name"]
            user_location = all_data["user"]["location"]
            user_coordinates = all_data["coordinates"]
            hashtags = all_data['entities']['hashtags']
            retweeted = all_data['retweeted']
            box = all_data['place']['bounding_box']['coordinates']

            if not check_user(username):
                du.insert_one(
                    {
                        'username': username,
                        'id': user_id,
                        'created_at': created_at,
                        'user_location': user_location,
                        'coordinates': str(user_coordinates),
                        'followers': followers,
                        'friends': friends,
                        'description': description,
                        'statuses_count': statuses_count,
                        'tweet': twerp,
                        'box': box
                    }
                )
                count = du.count()
                msg = Colour.White + 'Collected ' + Colour.Green + \
                    str(count) + Colour.White + ' users'
                spinner.text = msg

            if not retweeted:
                for hashtag in hashtags:
                    check_tag = hashtag['text']
                    check_tags(username, check_tag)

            if check_string(twerp, finds):
                db.winners.insert_one(
                    {
                        'username': username,
                        'id': user_id,
                        'created_at': created_at,
                        'user_location': user_location,
                        'coordinates': str(user_coordinates),
                        'followers': followers,
                        'friends': friends,
                        'description': description,
                        'statuses_count': statuses_count,
                        'tweet': twerp,
                        'box': box
                    }
                )
                if send_mail:
                    tweep = db.winners.find_one({'username': username})
                    twat = tweep['tweet'].encode()
                    twat = twat.decode('unicode-escape')
                    alert = "{} {}\n\n{}\n\nTwitter: https://twitter.com/{}\nLocation: {}\nDescription: {}\nStatus Count: {}\nFollowers: {}\nFollowing: {}\nAccount Age: {}".format(
                        name, email_msg, twat, username, user_location, description, statuses_count, followers, friends, created_at)
                    mailer(alert)
                if send_dm:
                    msg = Colour.Green + 'Sending DM to victim'
                    spinner.text = msg
                    api.send_direct_message(
                        user_id=user_id, text=dm_message)
            return True
        else:
            return True

    def on_error(self, status):
        spinner.stop()
        print(Colour.Red + str(status))


msg = Colour.White + 'Waiting for tweets...'
spinner = Halo(text=msg, spinner='dots')

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
twitterStream = Stream(auth, listener())
api = tweepy.API(auth)

try:
    spinner.start()
    twitterStream.filter(locations=box_boundary)
except Exception as e:
    spinner.stop()
    print(Colour.Red + str(e))
except KeyboardInterrupt:
    spinner.stop()
    sys.exit()
