import os, json, shutil
from zipfile import ZipFile


FOLDER_PATH = os.path.realpath(os.path.dirname(__file__))
SETTING = json.loads(open(f"{FOLDER_PATH}/auto_updatr_setting.json", "r").read())

def get_project_info(name: str="更新日誌", time: int=0) -> tuple[str, str, str, str]:
    with open(f"{FOLDER_PATH}/{name}.txt", 'r', encoding='utf-8') as file:
        texts = file.readlines()
        project_name = texts[0].split("-")[0]
        count = 0
        for i in range(len(texts)-1, -1, -1):
            if texts[i].count("=") > 15:
                count += 1
                if count == time+2:
                    project_data, project_time, project_version = texts[i+1].replace("版本", "").replace("\n", "").split("-") 
                    break
        else:
            raise Exception(f"Invalid file format: {name}.txt")
        return project_name, project_data, project_time, project_version

def get_all_file_paths(directory: str, no_zip_files: list[str]=[]) -> list[str]:

    file_paths = [] 
  
    for root, directories, files in os.walk(directory): 
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath) 

    file_paths = list(filter(lambda path: not any(path for no_zip_file in no_zip_files if no_zip_file in path), file_paths))

    return file_paths

def zipped(zipped_file_name: str, no_zip_files: list[str]=[]) -> int: 

    file_paths = get_all_file_paths(FOLDER_PATH, no_zip_files)


    print('Following files will be zipped:')
    for file_name in file_paths:
        print(file_name)
    
    with ZipFile(f"{zipped_file_name}.zip",'w') as zip:
        for file in file_paths: 
            zip.write(file) 
  
    print('All files zipped successfully!')
    return 0

def move_file(file_name: str, folder_name: str) -> int:
    try:
        shutil.move(f"{os.path.dirname(FOLDER_PATH)}/{file_name}",f"{os.path.dirname(FOLDER_PATH)}/{folder_name}/{file_name}")
        return 0
    except IsADirectoryError:
        print("Source is a file but destination is a directory.")
    except NotADirectoryError:
        print("Source is a directory but destination is a file.")
    except PermissionError:
        print("Operation not permitted.")
    except OSError as error:
        print(error)
    return 1

def change_folder_path_name(folder_name: str, project_name: str="None") -> int:
    if project_name == "None":
        project_name = FOLDER_PATH.split("/")[-1].split("-")[0]
    destination = f"{'/'.join(FOLDER_PATH.split('/')[:-1:])}/{project_name}-{folder_name}"
    if FOLDER_PATH == destination:
        print("Source and destination are the same.")
        return 0
    try:
        os.rename(FOLDER_PATH, destination)
        print("Rename successfully!(don't forget to reopen the new project folder.)")
        return 1
    except IsADirectoryError:
        print("Source is a file but destination is a directory.")
    except NotADirectoryError:
        print("Source is a directory but destination is a file.")
    except PermissionError:
        print("Operation not permitted.")
    except OSError as error:
        print(error)
    return 1

def rename() -> int:
    project_name, project_data, project_time, project_version = get_project_info()
    change_folder_path_name(project_version, project_name)
    return 0

def main() -> int:
    options = input("Chose following options (rename/zip):")
    if options.lower() == "rename":
        rename()
    elif options.lower() == "zip":
        zip_file_name = FOLDER_PATH.split("/")[-1]
        zipped(zip_file_name, SETTING["no_zip_files"])
        move_file(f"{zip_file_name}.zip", SETTING["zip_file_save_to"])
    return 0



if __name__ == "__main__":
    main()
else:
    raise Exception("Can not import this file in any approach.")