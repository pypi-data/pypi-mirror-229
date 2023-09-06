import os

def mapFileNameToUser(fileName):
    first_name, last_name, source_language, target_language, gender, email, uuid  = fileName.split("__")
    return {
        first_name,
        last_name,
        source_language,
        target_language,
        gender,
        email,
        uuid
    }


def createFolder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
	