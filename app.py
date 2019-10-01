import os
import shelve

from flask import Flask, render_template, request, redirect, url_for

from rq import Queue
from rq.job import Job
from worker import conn

import gspread
import pymongo
from oauth2client.service_account import ServiceAccountCredentials

# Start pymongo boilerplate
mongourl = "mongodb+srv://rolson:majetich1@w3-js-test-skugz.mongodb.net/test?retryWrites=true&w=majority"
mongo_client = pymongo.MongoClient(mongourl, 27017)
mongo_db = mongo_client.restaurant_db
mongo_rests = mongo_db.restaurants
mongo_menu_items = mongo_db.menu_items
# End pymongo boilerplate


# Start Gspread Boilerplate
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

spreadsheet = client.open("restaurant_db")
r_sheet = spreadsheet.worksheet("restaurants")  # Open the spreadhseet
m_sheet = spreadsheet.worksheet("menu_items")
# ENDGSPREAD


# Flask Boilerplate
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# End Flask Boilerplate

# rq (redis queue) boilerplate
q = Queue(connection=conn)
# End rq boilerplate

local_db = {}


@app.route('/', methods=["GET", "POST"])
def hello():
    return render_template('index.html')

@app.route('/<name>', methods=["GET", "POST"])
def hello_name(name):
    if request.method == "POST":
        input_field = request.form["url"]
        job = q.enqueue_call(
            func=expensive_compute, args=(input_field,), job_id=name, result_ttl=5000
        )
        print(job.get_id())
        return redirect(f"/results/{name}")

    else:
        return render_template('index.html', content=f"Hello {name}!", name=name)


@app.route("/results/<job_key>")
def get_job(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return render_template('index.html', content=f'Job (ID {job.id}) = {job.result}')

    else:
        return "Nay!", 202

@app.route("/downloadfrom/<target>")
def download_database(target):
    if target == "google":
        with shelve.open("localdata.dat") as shelf:
            for record in r_sheet.get_all_records():
                shelf[record["id"]] = record
            for record in m_sheet.get_all_records():
                shelf[record["id"]] = record

            local_db = dict(shelf)

    if target == "mongo":
        pass

    return render_template('index.html', content=str(local_db))

@app.route("/uploadto/<target>", methods=["GET", "POST"])
def upload_database(target):
    if request.method == "GET":
        return render_template("uploadconfirm.html", target=target)

    else:
        return "DELETED"


if __name__ == '__main__':
    print(os.environ['APP_SETTINGS'])
    app.run()
