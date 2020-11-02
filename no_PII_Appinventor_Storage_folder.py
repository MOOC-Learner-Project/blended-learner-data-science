import os
import hashlib


def hash_username(n):
    return hashlib.md5(n.encode('utf-8')).hexdigest()


def hash_foldername(n):
    folder_name = n.split('_')
    assert len(folder_name) > 1, folder_name
    assert folder_name[0] == 'ai'
    username = folder_name[1]
    if len(folder_name) > 2:
        username = '_'.join(folder_name[1:])
    
    n = '{}_{}'.format(folder_name[0], hash_username(username))
    return n


def hash_properties(n):
    data = []
    with open(n, 'r') as f:
        for line in f:
            data.append(line)

    if not data:
        return
    
    assert(data[0].startswith('main=appinventor.ai_')), data[0]
    main_element = data[0].split('=')[1].split('.')
    assert len(main_element) == 4
    username = hash_foldername(main_element[1])
    main_element[1] = username
    data[0] = 'main={}'.format('.'.join(main_element))
    with open(n, 'w') as f:
        for d in data:
            f.write(d)

            
def main(path):

    for root, dirs, files in os.walk(path):
        for _dir in dirs:
            if _dir.startswith('ai'):
                dst = hash_foldername(_dir)
                os.rename(os.path.join(root,_dir), os.path.join(root,dst))

        for _file in files:
            if _file == 'project.properties':
                hash_properties(os.path.join(root,_file))
                pass
            elif _file.endswith('.sqlite'):
                path = os.path.join(root, _file)
                os.remove(path)
                assert not os.path.exists(path)
                
if __name__ == '__main__':
    STORAGE_PATH = '../AppInventor_data/STORAGE'
    assert(os.path.exists(STORAGE_PATH))
    main(STORAGE_PATH)
