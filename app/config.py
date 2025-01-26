import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_URI = 'mysql+pymysql://user:userpassword@127.0.0.1:3306/tweets_db'
json_file = os.path.join(BASE_DIR, 'training_data/json/tweets.json')
txt_repository = os.path.join(BASE_DIR, 'training_data/txt')
