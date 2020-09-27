import logging
import mimetypes
import urllib.parse

from MediaLibraryManager.Sql.FileSystem import Directory, File
from MediaLibraryManager.Sql.LibraryImage import Image
from MediaLibraryManager.Sql.FileTags import Tag
from MediaLibraryManager.Sql.Main import create_database
from flask import Flask, render_template, send_file, request
from sqlalchemy.sql import text
from sqlalchemy.orm.exc import NoResultFound

from MediaLibraryManager.Sql.Scanning import DirectoryScan

app = Flask(__name__)
logger = logging.getLogger('MediaLibraryManager')


def setup_session():
    database_name = app.config['mlm-config'].db_name
    session = create_database(database_name)
    return session()


def get_list_subset(image_list, r):
    page = r.args.get('page') or 1
    page_results = r.args.get('page_results') or 50
    if r.args.get('all'):
        return image_list, None

    try:
        start = int(page_results) * (int(page) - 1)
        end = int(page_results) * int(page)
        return image_list[start:end], int(page)
    except ValueError:
        return image_list[0:50], 1


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
    images_subset, page = get_list_subset(db_images, request)

    return render_template('gallery.html', images=images_subset, page=page)


@app.route('/gallery/directory/<directory_id>')
def directory_gallery_id(directory_id):

    session = setup_session()
    try:
        db_dir = session.query(Directory).filter(Directory.id == directory_id).one()
    except NoResultFound:
        return directories()
    db_subdirs = session.query(File).filter(File.path.like(db_dir.path + '%')).distinct(File.path).\
        with_entities(File.path).all()
    processed_subdirs = []
    for sd in db_subdirs:
        root_path_url = '/gallery/directory/{}'.format(db_dir.id)
        psd = {'path_str': sd[0], 'path_url': '{}?sd='.format(root_path_url) + urllib.parse.quote_plus(sd[0])}
        if psd['path_str'] != db_dir.path:
            processed_subdirs.append(psd)
    query = text("select * from image inner join file on file_id = file.id "
                 "where path like :path")
    if request.args.get('sd') is not None:
        subdir_path = urllib.parse.unquote_plus(request.args.get('sd'))
        db_images = session.execute(query, {"path": subdir_path + "%"}).fetchall()
    else:
        db_images = session.execute(query, {"path": db_dir.path + "%"}).fetchall()
    images_subset, page = get_list_subset(db_images, request)

    return render_template('dir_gallery.html', images=images_subset, main_dir=db_dir.path, subdirs=processed_subdirs,
                           page=page)


# @app.route('/gallery/directory')
# def directory_gallery_path():
#
#     if request.args.get('path') is None:
#         return directories()
#
#     directory_path = urllib.parse.unquote_plus(request.args.get('path'))
#
#     session = setup_session()
#     db_subdirs = session.query(File).filter(File.path.like(directory_path + '%')).distinct(File.path).\
#         with_entities(File.path).all()
#     processed_subdirs = []
#     for sd in db_subdirs:
#         psd = {'path_str': sd[0], 'path_url': '/gallery/directory?path=' + urllib.parse.quote_plus(sd[0])}
#         if psd['path_str'] != directory_path:
#             processed_subdirs.append(psd)
#     query = text("select * from image inner join file on file_id = file.id "
#                  "where path like :path")
#     db_images = session.execute(query, {"path": directory_path+"%"}).fetchall()
#     images_subset, page = get_list_subset(db_images, request)
#
#     return render_template('dir_gallery.html', images=images_subset, main_dir=directory_path, subdirs=processed_subdirs,
#                            page=page)


@app.route('/images/view/<image_id>')
def image_view(image_id):

    session = setup_session()
    db_image = session.query(Image).filter(Image.id == image_id).one()

    prev_image_id = Image.find_prev_image_id(session, image_id)
    next_image_id = Image.find_next_image_id(session, image_id)

    return render_template('image_view.html', image=db_image, prev=prev_image_id, next=next_image_id)


@app.route('/images/manage/<image_id>', methods=['GET', 'POST'])
def image_manage(image_id):

    session = setup_session()
    db_image = session.query(Image).filter(Image.id == image_id).one()
    tag_types = Tag.get_types(session)
    if request.method == 'POST':
        # form data is passed as an immutable multi-dict and needs to be coerced into a more usable type
        form_data = {x: request.form[x] for x in request.form}
        db_image.file_info.add_tag_by_values(session, **form_data)
    file_tags = db_image.file_info.get_tags(session)

    return render_template('image_manage.html', image=db_image, file_tags=file_tags, tag_types=tag_types)


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
