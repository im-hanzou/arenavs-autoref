from eth_account import Account
import secrets
import requests
import json
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import time
import random
from datetime import datetime

init(autoreset=True)

DEFAULT_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,id;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://quest.arenavs.com',
    'referer': 'https://quest.arenavs.com/',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site'
}

TASKS = {
    1: {"name": "Follow Twitter", "link": "https://x.com/Arenaweb3", "reward": 30000},
    2: {"name": "Like & Retweet", "link": "https://x.com/Arenaweb3", "reward": 14000},
    3: {"name": "Invite Friends", "link": "https://x.com/Arenaweb3", "reward": 30000},
    4: {"name": "Join Discord", "link": "https://discord.gg/rAEr8EKZEZ", "reward": 20000}
}

def get_timestamp():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def log_message(wallet_num, message, color=Fore.WHITE):
    timestamp = get_timestamp()
    print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{timestamp}{Fore.WHITE}] [{Fore.CYAN}#{wallet_num}{Fore.WHITE}] {color}{message}")

def print_banner():
    banner = f"""{Fore.CYAN}
    ╔════════════════════════════════════════════════╗
    ║              ArenaVS Autoreferral              ║
    ║          https://github.com/im-hanzou          ║
    ╚════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def load_proxies(filename='proxies.txt'):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        log_message(0, f"{filename} not found!", Fore.RED)
        return []

def generate_wallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return private_key, acct.address

def get_random_proxy(proxies):
    if not proxies:
        return None
    return random.choice(proxies)

def register_wallet(wallet_address, referral_code, proxy, user_agent):
    url = "https://quest-api.arenavs.com/api/v1/users/initialize"
    
    headers = DEFAULT_HEADERS.copy()
    headers['user-agent'] = user_agent
    
    data = {
        "walletAddress": wallet_address,
        "referralCode": referral_code
    }
    
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    
    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
        return response.json()
    except Exception as e:
        return None

def complete_task(user_id, task_id, token, proxy, user_agent):
    url = f"https://quest-api.arenavs.com/api/v1/tasks/{task_id}/complete/{user_id}"
    
    headers = DEFAULT_HEADERS.copy()
    headers['user-agent'] = user_agent
    headers['authorization'] = f'Bearer {token}'
    
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    
    try:
        response = requests.post(url, headers=headers, json={}, proxies=proxies)
        return response.json()
    except Exception as e:
        return None

def get_user_data(wallet_address, token, proxy, user_agent):
    url = f"https://quest-api.arenavs.com/api/v1/users/{wallet_address}"
    
    headers = DEFAULT_HEADERS.copy()
    headers['user-agent'] = user_agent
    headers['authorization'] = f'Bearer {token}'
    
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        return response.json()
    except Exception as e:
        return None

def main():
    print_banner()
    
    proxies = load_proxies()
    if not proxies:
        log_message(0, "No proxies loaded, continuing without proxies", Fore.YELLOW)
    
    referral_code = input(f"{Fore.YELLOW}Enter your referral code: {Style.RESET_ALL}")
    print("")
    
    wallet_count = 0
    
    try:
        while True:
            wallet_count += 1
            
            private_key, wallet_address = generate_wallet()
            log_message(wallet_count, f"Generated new wallet: {Fore.MAGENTA}{wallet_address}", Fore.YELLOW)
            
            proxy = get_random_proxy(proxies)
            ua = UserAgent()
            user_agent = ua.chrome
            
            log_message(wallet_count, "Registering wallet...", Fore.YELLOW)
            reg_response = register_wallet(wallet_address, referral_code, proxy, user_agent)
            
            if not reg_response:
                log_message(wallet_count, "Registration failed", Fore.RED)
                continue
            
            user_id = reg_response['user']['id']
            token = reg_response['token']
            refcode = reg_response['user']['referralCode']
            
            log_message(wallet_count, "Registration successful!", Fore.GREEN)
            log_message(wallet_count, f"User ID: {user_id}", Fore.GREEN)
            
            
            for task_id, task_info in TASKS.items():
                task_name = task_info['name']
                reward = task_info['reward']
                
                log_message(wallet_count, f"Completing task {task_name} (Reward: {reward} XP)", Fore.YELLOW)
                result = complete_task(user_id, task_id, token, proxy, user_agent)
                
                if result and result.get('status'):
                    log_message(wallet_count, f"{task_name} completed successfully", Fore.GREEN)
                else:
                    log_message(wallet_count, f"Failed to complete {task_name}", Fore.RED)
            user_data = get_user_data(wallet_address, token, proxy, user_agent)
            
            if user_data:
                with open('accounts.txt', 'a') as f:
                    f.write(f"User ID: {user_id}\n")
                    f.write(f"Private Key: {private_key}\n")
                    f.write(f"Address: {wallet_address}\n")
                    f.write(f"Referral Code: {refcode}\n")
                    f.write(f"XP: {user_data.get('xp', 0)}\n\n")
                
                log_message(wallet_count, f"Referral to {Fore.GREEN}{referral_code}{Fore.MAGENTA} success. Saved to accounts.txt", Fore.MAGENTA)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program stopped by user. Total wallets registered: {wallet_count}")
        
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {str(e)}")
        
    finally:
        print(f"{Fore.GREEN}Program completed. Total wallets registered: {wallet_count}")

if __name__ == "__main__":
    main()
