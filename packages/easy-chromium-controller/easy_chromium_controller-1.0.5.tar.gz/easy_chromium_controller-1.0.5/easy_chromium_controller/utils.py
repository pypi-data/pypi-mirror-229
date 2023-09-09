import os
import wget
import psutil
import zipfile
import shutil

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
def Log(*args, **kwargs):
    print("🌐  >> " + "".join(map(str, args)), **kwargs)

def Input(start_of_line: str = ""):
    return input("🌐  >> " + start_of_line)

def KillAllChromiumProcessOnWindows():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'chromium.exe' in process.info['name']:
            try:
                psutil.Process(process.info['pid']).terminate()
            except Exception as e:
                pass

def KillAllChromiumProcessOnLinux():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'chromium' in process.info['name']:
            try:
                psutil.Process(process.info['pid']).terminate()
            except Exception as e:
                pass

def check_binary_files_istalled(binary_folder: str, path_to_driver : str):
    try:
        with open(binary_folder+path_to_driver, "r") as f:
            pass
    except Exception as e:
        try:
            updating = False
            for i,file_name in enumerate(os.listdir(binary_folder[:-10])):
                if 'bin-' in file_name:
                    if not updating: updating = True
                    shutil.rmtree(binary_folder[:-9] + file_name)
            if not updating: Log("Binary files not found. Installing...")
            else: Log("Binary files are outdated. Updating...")
            os.mkdir(binary_folder)
            # Descargar de github el archivo .zip
            print("Downloading binary files...")
            if "linux" in path_to_driver:
                path_to_zip_file = binary_folder+"/linux.zip"
                wget.download("https://github.com/gonfdez/easy-chromium-controller/releases/download/1.0.5/linux.zip", path_to_zip_file)
            else:
                path_to_zip_file = binary_folder+"\\win.zip"
                wget.download("https://github.com/gonfdez/easy-chromium-controller/releases/download/1.0.5/win.zip", path_to_zip_file)
            with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
                # Descomprimir el archivo .zip
                zip_ref.extractall(binary_folder)
            # Eliminar el archivo .zip
            os.remove(binary_folder+"\\win.zip")
            print('')
            Log("¡ Binary files installed !")
        except FileNotFoundError as e:
            raise Exception("Binary folder path is not valid.")
        