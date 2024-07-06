import os
import re
import sys
import shutil
import zipfile
import subprocess
import requests
import os.path
from packaging import version
from tqdm import tqdm

reload_prestart = False


def install_package(package_name):
    os.system(f'pip install {package_name}')
    global reload_prestart
    reload_prestart = True


def check_and_install_packages():
    packages = [
        ('tqdm', 'tqdm'),
        ('requests', 'requests'),
        ('cuda', 'cuda_python'),
        ('bettercam', 'bettercam'),
        ('numpy', 'numpy'),
        ('win32gui', 'pywin32'),
        ('ultralytics', 'ultralytics'),
        ('screeninfo', 'screeninfo'),
        ('asyncio', 'asyncio'),
        ('onnxruntime', 'onnxruntime onnxruntime-gpu'),
        ('serial', 'pyserial'),
        ('torch', '--pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124'),
        ('cv2', 'opencv-python')
    ]

    for module_name, package_name in packages:
        try:
            __import__(module_name)
        except ModuleNotFoundError:
            install_package(package_name)

    if reload_prestart:
        os.system('py helper.py')
        print('restarting...')
        quit()


def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open(filename, 'wb') as file:
        for data in response.iter_content(1024):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print('Error with downloading file.')


def upgrade_ultralytics():
    import ultralytics
    print('Checking for new ultralytics version...')
    ultralytics_current_version = ultralytics.__version__

    ultralytics_repo_version = requests.get(
        'https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/__init__.py'
    ).content.decode('utf-8')
    ultralytics_repo_version = re.search(r"__version__\s*=\s*\"([^\"]+)", ultralytics_repo_version).group(1)

    if ultralytics_current_version != ultralytics_repo_version:
        print('The versions of ultralytics do not match\nAn update is in progress...')
        os.system('pip install ultralytics --upgrade')
    else:
        os.system('cls')


def upgrade_pip():
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, text=True, check=True)
        current_version = result.stdout.split(' ')[1]

        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', '--dry-run'],
                                capture_output=True, text=True, check=True)
        latest_version = None
        for line in result.stdout.splitlines():
            if 'Collecting pip' in line:
                latest_version = line.split(' ')[-1].strip('()')
                break

        if latest_version and version.parse(current_version) < version.parse(latest_version):
            print(f'Current pip version: {current_version}')
            print(f'Upgrading pip to version: {latest_version}')
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        else:
            print('Pip is already up-to-date.')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def delete_files_in_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def find_cuda_path():
    cuda_paths = [path for key, value in os.environ.items() if key == 'PATH' for path in value.split(';') if
                  'CUDA' in path and '12.4' in path]
    return cuda_paths if cuda_paths else None


def install_tensorrt():
    if find_cuda_path():
        os.system('pip install tensorrt')
    else:
        print('First install Cuda')


def install_cuda():
    os.system('cls')
    print('Cuda 12.4 is being downloaded, and installation will begin after downloading.')
    # download_file(
    #     'https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda_12.4.0_551.61_windows.exe',
    #     './cuda_12.4.0_551.61_windows.exe')
    subprocess.call(f'{os.path.join(os.path.dirname(os.path.abspath(__file__)), "cuda_12.4.0_551.61_windows.exe")}')


def test_detections():
    import ultralytics
    from ultralytics import YOLO
    import cv2
    import win32gui, win32con
    cuda_support = ultralytics.utils.checks.cuda_is_available()
    if cuda_support:
        print('Cuda support True')
    else:
        print('Cuda is not supported\nTrying to reinstall torch with GPU support...')
        force_reinstall_torch()

    model = YOLO(f'models/gemborant.pt', task='detect')
    cap = cv2.VideoCapture('test_det.mp4')
    window_name = f'Model: gemborant.pt imgsz: 320'
    cv2.namedWindow(window_name)
    debug_window_hwnd = win32gui.FindWindow(None, window_name)
    win32gui.SetWindowPos(debug_window_hwnd, win32con.HWND_TOPMOST, 100, 100, 200, 200, 0)

    while cap.isOpened():
        success, frame = cap.read()
        if success:
            result = model(frame, stream=False, show=False, imgsz=320, verbose=False, conf=0.40)
            annotated_frame = result[0].plot()
            cv2.putText(annotated_frame, 'TEST 1234567890', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1,
                        cv2.LINE_AA)
            cv2.imshow(window_name, annotated_frame)
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


def force_reinstall_torch():
    os.system('pip uninstall torch torchvision torchaudio')
    os.system(
        'pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124')


def export_engine():
    from ultralytics import YOLO
    YOLO(f'models/gemborant.pt').export(format='engine')


def print_menu():
    os.system('cls')
    print("1: Download Cuda 12.4")
    print("2: Force reinstall Torch (Nightly-GPU)")
    print("3: Install TensorRT 10.0.1")
    print("4: Export engine format from model.pt to model.engine")
    print("5: Test the object detector")
    print("0: Exit")


def main():
    try:
        while True:
            print_menu()
            choice = input("Select an option: ")

            if choice == "1":
                install_cuda()
            elif choice == "2":
                force_reinstall_torch()
            elif choice == "3":
                install_tensorrt()
            elif choice == "4":
                export_engine()
            elif choice == "5":
                test_detections()
            elif choice == "0":
                print("Exiting the program...")
                break
            else:
                print("Incorrect input, try again.")
    except:
        quit()


if __name__ == "__main__":
    main()
