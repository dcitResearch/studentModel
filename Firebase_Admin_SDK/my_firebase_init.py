# typical firebase init ops
# work on making the package importable from anywhere

def init():
    print('Initializing Cloud Firestore...')

    import firebase_admin
    from firebase_admin import credentials, firestore

    # path to Admin SDK Private key
    # DON'T EVER SHARE OR ADD TO VERSION CONTROL

    path_to_credentials_file = "student-model-firebase-adminsdk-cijqi-42c9322af0.json"

    # contacting and initializing the Cloud Firestore database
    cred = credentials.Certificate(path_to_credentials_file)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    print('Initialization Complete...\n\n')

    return db


def main():
    return init()


if __name__ == '__main__':
    main()
