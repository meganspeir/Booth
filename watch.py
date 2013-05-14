import os
import hashlib
import shutil
import re

from uuid import uuid4
from unicodedata import normalize

from capture import app
from capture.database import db_session
from capture.models import Photo, Entries
from capture import exif

from config import WATCH_DIRECTORY, EXTENSIONS, DOMAIN, IMAGES_DIRECTORY, FILENAME_LENGTH


def good_extension(filename):
    """Only allow files that we say. Case insensitive"""
    return '.' in filename and \
        filename.lower().rsplit('.', 1)[1] in EXTENSIONS


def uniquify(file):
    """Creates a unique filename for each file."""
    extension = os.path.splitext(file)[1]
    hash = hashlib.sha1(unicode(uuid4()))
    filename = hash.hexdigest()[:FILENAME_LENGTH] + extension.lower()
    return filename


def get_date_time_original(filename):
    """Extracts the creation date of the photograph added by the camera, rather
     than the creation date of the photograph shown by the file system."""
    f = open(filename, 'rb')
    tags = exif.process_file(f, stop_tag='DateTimeOriginal')
    for tag in tags.keys():
        if tag in ('EXIF DateTimeOriginal'):
            return tags[tag]


def sanitize_date_time(metadata):
    """Sanitizes date in DateTimeOriginal EXIF data"""
    metadata = normalize('NFKD', unicode(metadata))\
        .encode('ascii', 'ignore').decode('ascii')
    metadata = re.sub(r'^(\d+):(\d+):', r'\1-\2-', metadata)
    return metadata


def insert_record(filename, metadata):
    """Inserts new record into databad with filename and metadata"""
    exists = Photo.query.filter(Photo.url == filename).count()
    if not exists:
        photo = Photo(url=filename,
                      date_time=sanitize_date_time(metadata))
        db_session.add(photo)
        db_session.commit()
        entry = Entries(photo_id=photo.id,
                        date_time=photo.date_time)
        db_session.add(entry)
        db_session.commit()


def move(source, destination):
    """Moves file so no further processing will take place"""
    dst = os.path.join(DOMAIN, IMAGES_DIRECTORY, destination)
    shutil.move(source, dst)


def watch(directory):
    """Does the shit above."""
    files = os.listdir(directory)
    path = [os.path.join(directory, file) for file in files]
    for file in path:
        if good_extension(file):
            filename = uniquify(file)
            date_time_original = get_date_time_original(file)
            insert_record(filename, date_time_original)
            move(file, filename)


def go():
    watch(WATCH_DIRECTORY)

if __name__ == "__main__":
    go()
