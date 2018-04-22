from app import app
from flask import Blueprint, request, Response, jsonify, redirect, session
from os.path import join
from werkzeug import secure_filename
from services.image_reg import is_trash_can
from tempfile import mkdtemp
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials
from config.main import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

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
        scope=['profile','email'],
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
        flow = OAuth2WebServerFlow(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, ['profile', 'email'])
        flow.redirect_uri = request.base_url
        credentials = None
        try:
            credentials = flow.step2_exchange(code)
        except Exception as e:
            pass

        print(credentials)
        if credentials:
            session['credentials'] = credentials.access_token

    return redirect('/')


@main.route('/validate-image', methods=['POST'])
def validate_image():
    tempdir = mkdtemp()
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
    return jsonify({ 'valid': sim[0], 'similarity': sim[1] }), 200