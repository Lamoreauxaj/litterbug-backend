from app import app
from flask import Blueprint, request, Response, jsonify, redirect, session
from flask.json import loads
from os.path import join
from werkzeug import secure_filename
from services.image_reg import is_trash_can
from tempfile import TemporaryDirectory
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials
from config.main import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from apiclient import discovery
from httplib2 import Http
from models.user import User
from app import db
from subprocess import call
import requests

main = Blueprint('main', __name__, template_folder='../views')

# session['credentials'] = credentials.access_token

@main.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, PUT'
    return response

@main.route('/', methods=['GET'])
def index():
    if app.debug:
        return redirect('http://localhost:8080/')
    return render_template('static/index.html')


@main.route('/login', methods=['GET'])
def login():
    flow = OAuth2WebServerFlow(client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scope=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri='http://localhost:5000/oauth2callback',
        approval_prompt='force',
        access_type='offline')

    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@main.route('/logout', methods=['GET'])
def logout():
    if not 'credentials' in session:
        return 'Not logged in', 200
    del session['credentials']
    return 'Logged out successfully', 200


@main.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    code = request.args['code']
    if code:
        flow = OAuth2WebServerFlow(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'])
        flow.redirect_uri = request.base_url
        credentials = None
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            pass

        if credentials:
            session['credentials'] = credentials.access_token
            userinfo = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': 'OAuth %s' % credentials.access_token}).text
            userinfo = (loads(userinfo))
            # print(userinfo)
            if User.query.filter_by(email=userinfo['email']).first():
                pass
            else:
                user = User(id=userinfo['id'],email=userinfo['email'],name=userinfo['name'],litterbug=0,picture=userinfo['picture'])
                db.session.add(user)
                db.session.commit()

    return redirect('/')


@main.route('/validate-image', methods=['POST'])
def validate_image():
    with TemporaryDirectory() as tempdir:
        file = None
        for f in request.files:
            file = request.files[f]
        if not file:
            return 'Not file found', 400
        # file = request.files[request.form['filename']]
        filename = secure_filename(file.filename)
        filepath = join(tempdir, filename)
        file.save(filepath)
        # print(filepath)
        sim = is_trash_can(filepath)
        # print(sim)
        # os.remove(filepath)
        # os.rmdir(tempdir)
        # call(['rm', filepath, '-r'])
    return jsonify({ 'valid': sim[0], 'similarity': sim[1] }), 200