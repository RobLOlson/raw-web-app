import os
from flask import Flask, render_template, request, redirect, url_for

from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

q = Queue(connection=conn)

@app.route('/', methods=["GET", "POST"])
def hello():
    return f"Hello World!<br>{os.environ['APP_SETTINGS']}"


@app.route('/<name>', methods = ["GET", "POST"])
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

def expensive_compute(my_input):
    return "INSIDE APP.PY"


if __name__ == '__main__':
    print(os.environ['APP_SETTINGS'])
    app.run()
