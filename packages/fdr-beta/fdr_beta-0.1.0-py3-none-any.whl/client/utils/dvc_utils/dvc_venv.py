import os
import subprocess
import shutil

def create_virtual_environment(target_path):
    """
    Venv creation on target dir & dvc install & progress bar
    """
    parent_dir = os.path.dirname(target_path)
    os.makedirs(parent_dir, exist_ok=True)

    venv_path = os.path.join(parent_dir, 'venv')

    subprocess.run(['python', '-m', 'venv', venv_path], 
                    check=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)

    
    activate_script = "activate" if os.name == "nt" else "activate"
    activate_path = os.path.join(venv_path, 'Scripts', activate_script)
    subprocess.run([activate_path], 
                    shell=True, 
                    check=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
    
    subprocess.run(['pip', 'install', 'dvc'], 
                    check=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
    
    return parent_dir

def delete_virtual_environment(parent_dir):
    """
    Venv deletion
    
    """
    venv_path = os.path.join(parent_dir, 'venv')
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path, 
                        onerror=lambda func, 
                        path, 
                        exc_info: None)
