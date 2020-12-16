import os

def delete_directory(path):
    for file in os.listdir(path):
        path_to_rm = os.path.join(path, file)
        print(path_to_rm)
        if os.path.isfile(path_to_rm):
            os.remove(path_to_rm)
        elif os.path.isdir(path_to_rm):
            delete_directory(path_to_rm)
        else:
            raise Exception
    os.rmdir(path)
