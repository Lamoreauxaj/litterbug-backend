from flask import Blueprint, request, Response, jsonify
from os.path import join
from werkzeug import secure_filename
from services.image_reg import is_trash_can
from tempfile import mkdtemp

main = Blueprint('main', __name__, template_folder='../views')


@main.route('/validate-image', methods=['POST'])
def validate_image():
    if 'filename' not in request.form:
        return 'Must include filename', 400
    if request.form['filename'] not in request.files:
        return 'Must include file', 400
    tempdir = mkdtemp()
    file = request.files[request.form['filename']]
    filename = secure_filename(file.filename)
    filepath = join(tempdir, filename)
    file.save(filepath)
    # print(filepath)
    sim = is_trash_can(filepath)
    # print(sim)
    return jsonify({ 'valid': sim[0], 'similarity': sim[1] }), 200