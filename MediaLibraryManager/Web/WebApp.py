import logging
import mimetypes

from MediaLibraryManager.Sql.FileSystem import DirectorySql, FileSql
from MediaLibraryManager.Sql.LibraryImage import LibraryImage
from MediaLibraryManager.Sql.Main import create_database
from flask import Flask, render_template, send_file

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
    db_directories = session.query(DirectorySql).all()

    return render_template('directories.html', directories=db_directories)


@app.route('/directory_scans')
def directory_scans():

    session = setup_session()
    db_scans = session.query(DirectoryScan).all()

    return render_template('directory_scans.html', scans=db_scans)


@app.route('/images')
def images():

    session = setup_session()
    db_images = session.query(LibraryImage, FileSql).filter(LibraryImage.file_id == FileSql.id).all()

    return render_template('images.html', images=db_images)


@app.route('/images/id/<image_id>')
def serve_image(image_id):

    session = setup_session()
    db_image = session.query(LibraryImage, FileSql).filter(LibraryImage.id == image_id).\
        filter(LibraryImage.file_id == FileSql.id).one()

    return send_file(db_image.FileSql.path + db_image.FileSql.filename,
                     mimetypes.guess_type(db_image.FileSql.filename)[0])
