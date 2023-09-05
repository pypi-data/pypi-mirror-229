# Libraries
from ...utils.utils import print_lines_per_terminal_size
from ...utils.cmd_utils.cmd_main import clear
from ...classes.DatasetManager import DatasetManager
from termcolor import cprint
from ...utils.utils import dir_picking, check_dvc_file, sample_headers, sample_data
from ...utils.dvc_utils.dvc_ops import dvc_pipeline

# FDR Information Section
def get_operations_info():
    """
    Display download actions info section
    """
    print_lines_per_terminal_size()
    print("Useful commands:")
    print_lines_per_terminal_size()
    print("- fdr pull   -->  download dataset    ,args: [--name/-n]")
    print("- fdr push   -->  upload dataset      ,args: None")
    print("- fdr show   -->  show all datasets   ,args: None")
    print("- fdr doc    -->  show documentation  ,args: None")
    print("- fdr clear  -->  clear fdr terminal  ,args: None")
    print("- fdr menu   -->  exit to menu        ,args: None")
    print("- fdr log    -->  show history        ,args: [--save/-s]")
    print_lines_per_terminal_size()

def fdr_clear(page_title:str):
    """
    FDR clear command
    """
    clear()
    cprint(f'\n{page_title}\n', 'cyan', attrs=['bold'])
    get_operations_info()

def fdr_log_save():
    """
    FDR log command --save||-s
    """
    # dir picking:
    folder_path = dir_picking('Please select a dataset folder to save the history of FDR commands')
    
    # return non-null dir
    if not folder_path:
        print("No folder selected. Operation canceled.")
        return None
    else:
        print(f"Saved successfully at: '{folder_path}/fdr_logs.txt'")

    return folder_path

def fdr_push():
    """
    FDR push command
    """
    # Pick dataset dir
    folder_path = dir_picking(message='Please select a dataset folder to upload to remote FDR repository')

    # DVC push
    if folder_path:
        cprint(f'\nPushing "{folder_path}" to FaradAI remote storage', "yellow", attrs=['bold'])
        dvc_pipeline(folder_path, action="push", dvc_image=None)
        cprint(f'Done!', "green", attrs=['bold'])
    else:
        cprint("No folder selected. Operation canceled.", "red", attrs=['bold'])

def fdr_pull(args):
    """
    FDR pull command
    """
    # init name
    dataset_name = None

    # handle dir picking and dvc
    if args:
        if '--name' in args or '-n' in args:
            name_index = args.index('--name') if '--name' in args else args.index('-n')
            if len(args) >= name_index + 2:
                dataset_name = args[name_index + 1]

                # Check dataset availability
                manager = DatasetManager(data=sample_data(), headers=sample_headers())
                dataset_names = manager.get_dataset_names()

                if dataset_name in dataset_names:

                    # Choose dir to save dataset
                    folder_path = dir_picking(message='Select a target folder to download dataset from remote FDR repository')

                    if folder_path and check_dvc_file(folder_path):
                    # DVC pull --name
                        cprint(f'\nPulling "{dataset_name}" from FaradAI remote storage to "{folder_path}"', "yellow", attrs=['bold'])
                        dvc_pipeline(folder_path, action="pull", dvc_image=dataset_name)
                        cprint(f'Done!', "green", attrs=['bold'])
                    elif not folder_path:
                        cprint("No folder selected. Operation canceled.", "red", attrs=['bold'])
                    elif not check_dvc_file(folder_path):
                        cprint(".dvc file does not exist or is corrupt.", "red", attrs=['bold'])

                else:
                    cprint(f'Dataset does not exist in remote FDR repository or access is denied', 
                           "red", 
                           attrs=['bold'])

    # return dataset name
    if dataset_name:
        return dataset_name

    else:
        print("Invalid argument. Please specify dataset name [--name/-n]")
        return None