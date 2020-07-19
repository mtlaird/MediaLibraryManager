import logging
import mimetypes
import urllib.parse

from MediaLibraryManager.Sql.FileSystem import Directory, File
from MediaLibraryManager.Sql.LibraryImage import Image
from MediaLibraryManager.Sql.Main import create_database
from flask import Flask, render_template, send_file, request

from MediaLibraryManager.Sql.Scanning import DirectoryScan

app = Flask(__name__)
logger = logging.getLogger('MediaLibraryManager')


def setup_session():
    database_name = app.config['mlm-config'].db_name
    session = create_database(database_name)
    return session()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/files')
def files():
    session = setup_session()
    # TODO: Refactor to use ORM and foreign keys
    db_files = session.execute("select * from files f left outer join images on f.id = images.file_id "
                               "where images.id is null;")
    return render_template('files.html', files=db_files)


@app.route('/directories')
def directories():

    session = setup_session()
    db_directories = Directory.select_all(session)

    return render_template('directories.html', directories=db_directories)


@app.route('/directory_scans')
def directory_scans():

    session = setup_session()
    db_scans = session.query(DirectoryScan).all()

    return render_template('directory_scans.html', scans=db_scans)


@app.route('/images')
def images():

    session = setup_session()
    db_images = Image.select_all(session)

    return render_template('images.html', images=db_images)


@app.route('/gallery')
def image_gallery():

    session = setup_session()
    db_images = Image.select_all(session)

    return render_template('gallery.html', images=db_images)


@app.route('/gallery/directory/<directory_id>')
def directory_gallery_id(directory_id):

    session = setup_session()
    db_dir = session.query(Directory).filter(Directory.id == directory_id).one()
    db_subdirs = session.query(File).filter(File.path.like(db_dir.path + '%')).distinct(File.path).\
        with_entities(File.path).all()
    processed_subdirs = []
    for sd in db_subdirs:
        psd = {'path_str': sd[0], 'path_url': '/gallery/directory?path=' + urllib.parse.quote_plus(sd[0])}
        if psd['path_str'] != db_dir.path:
            processed_subdirs.append(psd)
    db_images = session.query(Image, File).filter(Image.file_id == File.id)\
        .filter(File.path.like(db_dir.path + '%'))

    return render_template('dir_gallery.html', images=db_images, main_dir=db_dir.path, subdirs=processed_subdirs)


@app.route('/gallery/directory')
def directory_gallery_path():

    directory_path = urllib.parse.unquote_plus(request.args.get('path'))

    session = setup_session()
    db_subdirs = session.query(File).filter(File.path.like(directory_path + '%')).distinct(File.path).\
        with_entities(File.path).all()
    processed_subdirs = []
    for sd in db_subdirs:
        psd = {'path_str': sd[0], 'path_url': '/gallery/directory?path=' + urllib.parse.quote_plus(sd[0])}
        if psd['path_str'] != directory_path:
            processed_subdirs.append(psd)
    db_images = session.query(Image, File).filter(Image.file_id == File.id)\
        .filter(File.path.like(directory_path + '%'))

    return render_template('dir_gallery.html', images=db_images, main_dir=directory_path, subdirs=processed_subdirs)


@app.route('/images/view/<image_id>')
def image_view(image_id):

    session = setup_session()
    db_image = session.query(Image).filter(Image.id == image_id).one()

    return render_template('image_view.html', image=db_image)


@app.route('/images/id/<image_id>')
def serve_image(image_id):

    session = setup_session()
    db_image = session.query(Image).filter(Image.id == image_id).one()

    return send_file(db_image.file_info.path + db_image.file_info.filename,
                     mimetypes.guess_type(db_image.file_info.filename)[0])


@app.route('/thumbnails/id/<image_id>')
def serve_thumbnail(image_id):

    session = setup_session()
    db_image = session.query(Image).filter(Image.id == image_id).one()

    return send_file(db_image.thumbnail_path, mimetypes.guess_type(db_image.file_info.filename)[0])
