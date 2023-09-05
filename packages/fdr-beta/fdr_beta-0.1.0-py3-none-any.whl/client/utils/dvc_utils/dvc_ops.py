import os
import time
import subprocess
from tqdm import tqdm
from ...utils.utils import progress_update

def dvc_init(parent_dir):
    """
    Initialize DVC in current wd
    """
    dvc_init_cmd = ['dvc', 'init', '--no-scm', '-f']
    subprocess.run(dvc_init_cmd, check=True, cwd=parent_dir, shell=True, 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)

def dvc_analytics_off(parent_dir):
    """
    Disable DVC analytics
    """
    dvc_analytics_off_cmd = ['dvc', 'config', 'core.analytics', 'false']
    subprocess.run(dvc_analytics_off_cmd, check=True, cwd=parent_dir, 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)


def dvc_remote(parent_dir):
    """
    Set DVC remote
    """
    dvc_add_remote = ["dvc", "remote", "add", "--default", "drive",
                      "gdrive://1YVePRVMrdkyKQgzBci_vLNhhw6GnAE8M"]
    subprocess.run(dvc_add_remote, check=True, cwd=parent_dir, 
                       stdout=subprocess.DEVNULL)
    
    dvc_acknowledge_abuse = ["dvc", "remote", "modify", "drive",
                             "gdrive_acknowledge_abuse", "true"]
    subprocess.run(dvc_acknowledge_abuse, check=True, cwd=parent_dir, 
                       stdout=subprocess.DEVNULL)

def dvc_add(parent_dir, dir):
    """
    Add target to DVC cache
    """
    # Add
    dvc_add = ["dvc", "add", f"{dir}"]
    subprocess.run(dvc_add, check=True, cwd=parent_dir, shell=True,
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
    
def dvc_push(parent_dir, workers):
    """
    Push to DVC remote
    """
    # Push
    dvc_push = ["dvc", "push", f"-j {workers}"]
    subprocess.run(dvc_push, check=True, cwd=parent_dir, shell=True,
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    
def dvc_pull(dir, dvc_image):
    """
    Pull dataset from remote based on .dvc file
    """
    dvc_fetch = ["dvc", "fetch", f'{dvc_image}.dvc']
    subprocess.run(dvc_fetch, check=True, cwd=dir, shell=True,
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
    dvc_pull = ["dvc", "checkout", f'{dvc_image}.dvc']
    subprocess.run(dvc_pull, check=True, cwd=dir, shell=True,
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)

def dvc_destroy(parent_dir):
    """
    Uninitialize DVC in current wd by force
    """
    dvc_destroy = ["dvc", "destroy", "--force"]
    subprocess.run(dvc_destroy, check=True, cwd=parent_dir, shell=True,
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
    
def dvc_retry_with_backoff(func, max_retries=5, retry_delay=10):
    """
    Retry mechanism for dvc methods
    """
    for retry in range(max_retries):
        try:
            func()
            break
        except Exception as e:
            print(f"Attempt {retry + 1} failed. Error: {e}")
            if retry < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Maximum retries ({max_retries}) reached.")
                raise

def dvc_pipeline(target_dir, action, dvc_image):
    """
    Main DVC Operation Pipeline
    """
    with tqdm(total=100, unit="%") as pbar:

        # initial pbar update
        progress_update(pbar, 5)

        # get cwd & parent
        parent_dir = os.path.dirname(target_dir)
        progress_update(pbar, 5)

        # dvc init
        dvc_init(parent_dir)
        progress_update(pbar, 5)

        # dvc disable analytics
        dvc_analytics_off(parent_dir)
        progress_update(pbar, 5)
        
        # dvc remote
        dvc_remote(parent_dir)
        progress_update(pbar, 5)

        # dvc action
        if action == "push":
            # add
            dvc_add(parent_dir, target_dir)
            # push & retry mechanism
            dvc_retry_with_backoff(lambda: dvc_push(parent_dir,
                                                    workers=8))

            
        elif action == "pull":
            # pull & retry mechanism
            dvc_retry_with_backoff(lambda: dvc_pull(target_dir, 
                                                    dvc_image))

        # dvc destroy
        progress_update(pbar, 50)
        dvc_destroy(parent_dir)
        progress_update(pbar, 24)

        # venv destroy
        progress_update(pbar, 1)