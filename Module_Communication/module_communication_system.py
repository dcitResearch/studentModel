# only useful xml files in a course dir are:
#     course.xml
#     enrollments.xml
#     inforef.xml
#     roles.xml
#     files.xml
#     grade_history.xml
#     gradebook.xml
#     roles.xml
#     users.xml

# NOTE:
#     * any variable/object in msc can be referenced by msc.foo

# TODO
# optimize this using transactions and batched writes
# add in exception handling
# classes??
# course times are critical


# initializing module_communication_system
print('Module Communication System initialization beginnning...')

# imports
print('Importing firebase admin...')
import firebase_admin
from firebase_admin import credentials, firestore, storage

print('Importing pprint...')
import pprint
pp = pprint.PrettyPrinter(indent=4)

print('Importing xmltodict...')
import xmltodict

print('Importing json...')
import json

print('Importing time...')
import time

print('Importing re (regex)...')
import re


# this function connects to:
    # cloud firestore and returns the database object, db
    # firebase storage and returns the bucket object, bucket
    # handling buckets in python: https://cloud.google.com/storage/docs/reference/libraries#client-libraries-usage-python
        # https://cloud.google.com/storage/docs/uploading-objects?authuser=0#storage-upload-object-python
def init_firebase(path_to_credentials_file = "../Firebase_Admin_SDK/student-model-firebase-adminsdk-cijqi-42c9322af0.json"):

    # path to Admin SDK Private key
    # DON'T EVER SHARE OR ADD TO VERSION CONTROL

    # contacting and initializing the Cloud Firestore database

    cred = credentials.Certificate(path_to_credentials_file)
    firebase_admin.initialize_app(cred, {
            'storageBucket': 'student-model.appspot.com'
        }
    )

    print('Connecting to cloud firestore...')
    db = firestore.client()
    print('Connection to cloud firestore successful!')

    print('Connecting to storage...')
    bucket = storage.bucket()
    print('Connection to cloud storage successful!')

    print('Module Communication System successfully initialized.\n\n')

    return db, bucket


# # connects to cloud firestore
db, bucket = init_firebase()
# print('Module Communication System successfully initialized.')

# testing the connection
# doc_ref = db.document(u'students/816000772')
# print(doc_ref.get().to_dict())


# adds course information from xml file
# this is called later down
# local_path_to_course_directory must have the '/' at the end
def add_course_from_xml(local_path_to_course_directory):

    # parsing xml
    # path_to_course_xml_file = '../../Testing_Area_For_Anonymized_Moodle_Data/COMP2500_201720-A/course/course.xml'
    local_path_to_course_xml_file = local_path_to_course_directory + 'course/course.xml'
    with open(local_path_to_course_xml_file) as fd:
        doc = json.loads(json.dumps(xmltodict.parse(fd.read(), process_namespaces=True)))

    # pp = pprint.PrettyPrinter(indent=1)
    # pp.pprint(doc['course'])

    # writing to cloud firestore
    global db
    doc_path = u'courses/' + doc['course']['idnumber']
    doc_ref = db.document(doc_path)
    print('Writing to {}'.format(doc_path))
    doc_ref.set(doc)
    doc_ref.update({
        'attendance_sheets': []
    })

    cloud_path_to_course_xml_file = doc_path
    local_path_to_students_xml_file = local_path_to_course_directory + 'users.xml'
    add_students_from_xml(cloud_path_to_course_xml_file, local_path_to_students_xml_file)


# add students from xml
# this is called from the add_course_from_xml function
# TODO need to filter out role 5's
def add_students_from_xml(cloud_path_to_course_xml_file = None, local_path_to_students_xml_file = None):

    # parsing xml
    with open(local_path_to_students_xml_file) as fd:
        doc = json.loads(json.dumps(xmltodict.parse(fd.read(), process_namespaces=True)))

    pp = pprint.PrettyPrinter(indent=1)

    # adding usernames to course document
    # currently considering the user id attribute in tag to be the student's id
    usernames = [user['@id'] for user in doc['users']['user']]
    # pp.pprint(usernames)

    doc_ref = db.document(cloud_path_to_course_xml_file)
    print('Writing user ids to course document...')
    doc_ref.update({
        'users': usernames
    })

    # adding users to student collection
    # TODO need to sort out duplicate overwriting
    for user in doc['users']['user']:
        user['signatures'] = []
        user['faces'] = []
        cloud_path_to_student_document = u'students/'+user['@id']
        print('Writing to {}'.format(cloud_path_to_student_document))
        doc_ref = db.document(cloud_path_to_student_document).set(user)
    print('All students written successfully...')



# uploads scanned .jpg of attendance_file (roll sheet) to cloud Firestore in the correct course
# uses time in ticks as the .jpg id
def upload_attendance_file(cloud_course_document_id = 'COMP2500_201720', timestamp = time.time(), local_path_to_attendance_file = '..\\..\\Testing_Area_data_from_Jimmel_Handwriting\\dcitSignatureRecognition\\TemplateTest\\form2.jpg'):

    # read in scanned attendance_file (.jpg)
    with open(local_path_to_attendance_file, 'rb') as input_file:
        attendance_file = input_file.read()

    doc_path = u'courses/'+cloud_course_document_id+'/attendance_files/'+str(timestamp)
    doc_ref = db.document(doc_path)

    # uploading attendance_file
    print('Uploading attendance file...')
    doc_ref.set({
        'attendance_file': attendance_file
    })
    print('Upload successful...')

# upload_attendance_file()

# downloading all attendance files in a collection
def download_all_attendance_files(cloud_course_document_id = 'COMP2500_201720'):
    collec_path = u'courses/'+cloud_course_document_id+'/attendance_files'
    collec = db.collection(collec_path).get()

    for doc in collec:
        file_name = doc.id+'.jpg'
        print('downloading {}'.format(file_name))
        with open(file_name, 'wb') as output_file:
            output_file.write(doc.to_dict()['attendance_file'])

# download_all_attendance_files()


# =========================== TEST DUPLICATE .jpg SIGNATURE FILE GENERATION (TO REMOVE) ===========================
from os import listdir
from os.path import isfile, join

def get_file_list_in_path(mypath = '.'):
    return [f for f in listdir(mypath) if isfile(join(mypath, f)) and re.match('([^\s]+(\.(?i)(jpg|png|gif|bmp))$)', f) is not None]


def duplicate(course_name = 'COMP2500_201720', test_pic_dir_path = '../../Testing_Area_data_from_Jimmel_Handwriting/'):

    # getting list of users for the course
    usernames_file_path = 'courses/'+course_name
    course = db.document(usernames_file_path).get().to_dict()

    print(course['users'])

    # reading the test pic
    test_pic_path = test_pic_dir_path+'test_pic.jpg'
    with open(test_pic_path, 'rb') as input:
        test_pic = input.read()

    # writing duplicates
    for user in course['users']:
        out_file_path = test_pic_dir_path + user + '.jpg'
        with open(out_file_path, 'wb') as out:
            out.write(test_pic)

# duplicate()
# =========================== TEST DUPLICATE FILE GENERATION (TO REMOVE) ===========================


# corrected signature -> signatures
def upload_student_signatures_to_cloud_firestore(path_to_signatures = '../../Testing_Area_data_from_Jimmel_Handwriting/'):

    # regex for getting file list in the directory
    onlyfiles = [f for f in listdir(path_to_signatures) if isfile(join(path_to_signatures, f)) and re.match('([^\s]+(\.(?i)(jpg|png|gif|bmp))$)', f) is not None]

    # reading all files in the directory and writing to cloud firestore in the respective student document
    for file_name in onlyfiles:
        file_path = path_to_signatures+file_name
        with open(file_path, 'rb') as input_file:
            signature = input_file.read()

        student_id = file_name.strip('.jpg')
        cloud_path = 'students/'+student_id+'/signatures'
        print('Uploading to {}'.format(cloud_path))
        db.collection(cloud_path).add({
            'signature': signature
        })
    print('Uploads complete')


# upload_student_signatures_to_cloud_firestore()

# downloads and stores (as .jpg) all signatures for a given student id
# from cloud firestore
def download_student_signatures(student_id):

    # resolving blob path
    cloud_path_to_student_signatures = 'students/'+student_id+'/signatures'
    signatures = db.collection(cloud_path_to_student_signatures).get()

    # traversing collections to write to local disk
    for signature in signatures:
        file_name = signature.id+'.jpg'
        print('Downloading {}'.format(signature.id))
        with open(file_name, 'wb') as output_file:
            output_file.write(signature.to_dict()['signature'])

# download_student_signatures('10000')


    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


# ============================================================================ USING STORAGE
# uploads any blob to storage
def upload_blob(bucket, source_file_path, destination_blob_path):
    """Uploads a file to the bucket."""
    blob = bucket.blob(destination_blob_path)

    blob.upload_from_filename(source_file_path)

    print('File {} uploaded to {}.'.format(
        source_file_path,
        destination_blob_path))


# downloads blob from storage
def download_blob(bucket, source_blob_path, destination_file_path):
    """Downloads a blob from the bucket."""
    blob = bucket.blob(source_blob_path)

    blob.download_to_filename(destination_file_path)

    print('Blob {} downloaded to {}.'.format(
        source_blob_path,
        destination_file_path))



# sends a single student's signature to cloud storage
'''
LOGIC:
    if array doesnt exist:
        set blob and signature name to XXXXX_signatures_1
    else:
        read length of Array
        add new signature name to Array

    add blob
'''
def upload_student_signature_to_cloud_storage(student_id, local_path_to_signature):
    """Uploads a student signature .jpg file to the bucket."""

    # getting student document from cloud firestore
    cloud_firestore_document_path = 'students/'+student_id
    doc_ref = db.document(cloud_firestore_document_path)
    student = doc_ref.get().to_dict()
    signatures = student['signatures']

    # updating the signature list in cloud Firestore
    file_name = student_id+'_signature_'+str(time.time())
    signatures.append(file_name)
    doc_ref.update({
        'signatures': signatures
    })

    # saving to cloud storage
    storage_path_to_signature = 'students/'+student_id+'/signatures/'+file_name
    upload_blob(bucket, local_path_to_signature, storage_path_to_signature)


def upload_student_signatures_for_courses_to_cloud_storage(course_id, local_path_to_signatures = '../../Testing_Area_data_from_Jimmel_Handwriting/demo_data_18_9_7/lists/List1/'):
    users = get_students_enrolled_in_course(course_id)
    file_list = 




def download_student_signatures_from_cloud_storage(student_id, local_directory_to_save = 'D:\DELL STORAGE\Google Drive\Research Project\Chris\\'):

    # getting the current number of signatures saved from cloud firestore
    cloud_path_to_student_document = 'students/'+student_id
    doc_ref = db.document(cloud_path_to_student_document)
    student = doc_ref.get().to_dict()
    num_signatures = student['signatures']

    # looping through all the signatures for the student and storing in local_directory_to_save
    for i in range(1, num_signatures+1):
        blob_name = student_id+'_signature_'+str(i)
        source_blob_path = 'students/'+student_id+'/signatures/'+blob_name
        destination_file_path = local_directory_to_save+blob_name+'.jpg'
        download_blob(bucket, source_blob_path, destination_file_path)


def get_students_enrolled_in_course(course_code):
    cloud_path_to_course_doc = 'courses/'+course_code
    doc_ref = db.document(cloud_path_to_course_doc)
    course = doc_ref.get().to_dict()
    users = course['users']
    return users


def get_attendance_sheet_names_for_course(course_code):
    cloud_path_to_course_doc = 'courses/'+course_code
    doc_ref = db.document(cloud_path_to_course_doc)
    course = doc_ref.get().to_dict()
    attendance_sheets = course['attendance_sheets']
    return attendance_sheets


def upload_attendance_sheet_to_cloud_storage(course_code, local_path_to_attendance_sheet):
    # updating cloud firestore
    cloud_firestore_path_to_course_doc = 'courses/'+course_code
    doc_ref = db.document(cloud_firestore_path_to_course_doc)
    course = doc_ref.get().to_dict()
    attendance_sheets = course['attendance_sheets']
    file_name = course_code+'_attendance_sheet_'+str(time.time())
    attendance_sheets.append(file_name)
    doc_ref.update({
        'attendance_sheets': attendance_sheets
    })

    # update cloud storage
    cloud_storage_path_to_course = cloud_firestore_path_to_course_doc + '/attendance_sheets/' + file_name
    upload_blob(bucket, local_path_to_attendance_sheet, cloud_storage_path_to_course)


# currently modified to download only one attendance sheet
# use time field to determine which attendance sheet is to be downloaded
def download_attendance_sheet_from_cloud_storage(course_code, time = None, local_path_to_save_file = 'D:\DELL STORAGE\Google Drive\Research Project\Chris\\'):
    attendance_sheets = get_attendance_sheet_names_for_course(course_code)
    file_name = attendance_sheets[0]
    cloud_storage_path_to_blob = 'courses/'+course_code+'/attendance_sheets/'+file_name
    local_path_to_save_file += file_name+'.jpg'
    download_blob(bucket, cloud_storage_path_to_blob, local_path_to_save_file)
