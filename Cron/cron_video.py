# importing the required modulesimport osimport reimport time# main functiondef delete_vid():    # initializing the count    deleted_files_count = 0    # specify the path    path = os.path.join(os.getcwd(), 'Test_Cases', "Test_output", 'Videos')    webm_regex = re.compile(f'.*.webm$''.*.mp4$')    for root_dir, folder, files in os.walk(path):        for file in files:            if webm_regex.match(file):                print(file)    print(path)    # specify the days    days = 0.25    # converting days to seconds    # time.time() returns current time in seconds    seconds = time.time() - (days * 24 * 60 * 60)    try:        # checking whether the file is present in path or not        if os.path.exists(path):            # iterating over each and every folder and file in the path            for root_folder, folders, files in os.walk(path):                for file in files:                    # file path                    file_path = os.path.join(root_folder, file)                    # comparing the days                    if seconds >= get_file_or_folder_age(file_path):                        # invoking the remove_file function                        remove_file(file_path)                        deleted_files_count += 1  # incrementing count        else:            # file/folder is not found            print(f'"{path}" is not found')    except FileNotFoundError as FNF:        print(FNF)    print(f"Total files deleted: {deleted_files_count}")def remove_file(path):    # removing the file    if not os.remove(path):        # success message        print(f"{path} is removed successfully")    else:        # failure message        print(f"Unable to delete the {path}")def get_file_or_folder_age(path):    # getting ctime of the file/folder    # time will be in seconds    ctime = os.stat(path).st_ctime    # returning the time    return ctimeif __name__ == '__main__':    delete_vid()