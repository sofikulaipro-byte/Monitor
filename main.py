import requests
import time
import os

# ==========================================
# এখানে আপনার তথ্যগুলো বসান (ডাবল কোটেশনের ভেতরে)
# ==========================================
USER_CONFIG = {
    "GITHUB_TARGET_USER": "target_username",  # যার গিটহাব থেকে চুরি/কপি করবেন তার নাম
    "MY_GITHUB_TOKEN": "ghp_xxxxxxxxxxxx",    # আপনার গিটহাব টোকেন (ধাপ ২ থেকে পাওয়া)
    "BOT_TOKEN": "8543918845:AAH3NORv4MJhb6_ywUsRPP-K0BIqr-p50S0",           # আপনার টেলিগ্রাম বট টোকেন (ধাপ ১ থেকে পাওয়া)
    "CHAT_ID": "123456789",                   # আপনার চ্যাট আইডি (ধাপ ১ থেকে পাওয়া)
    "CHECK_TIME": 15                          # কত সেকেন্ড পর পর চেক করবে
}
# ==========================================

def send_msg(text):
    """টেলিগ্রামে মেসেজ পাঠানোর ফাংশন"""
    url = f"https://api.telegram.org/bot{USER_CONFIG['BOT_TOKEN']}/sendMessage"
    try:
        requests.post(url, json={"chat_id": USER_CONFIG['CHAT_ID'], "text": text})
    except:
        pass

def send_file(filename, caption):
    """টেলিগ্রামে ফাইল পাঠানোর ফাংশন"""
    url = f"https://api.telegram.org/bot{USER_CONFIG['BOT_TOKEN']}/sendDocument"
    try:
        with open(filename, 'rb') as f:
            data = {'chat_id': USER_CONFIG['CHAT_ID'], 'caption': caption}
            files = {'document': f}
            print(f"Uploading {filename}...")
            requests.post(url, data=data, files=files)
    except Exception as e:
        print(f"Upload Error: {e}")

def get_repos():
    """টার্গেট ইউজারের রিপোজিটরি লিস্ট চেক করা"""
    url = f"https://api.github.com/users/{USER_CONFIG['GITHUB_TARGET_USER']}/repos?sort=created&direction=desc"
    headers = {"Authorization": f"token {USER_CONFIG['MY_GITHUB_TOKEN']}"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def main():
    print("Bot Started...")
    send_msg(f"🤖 Bot is Active! Monitoring: {USER_CONFIG['GITHUB_TARGET_USER']}")
    
    # শুরুতে যেগুলো আছে সেগুলো যাতে ডাউনলোড না করে, তাই লিস্টে রেখে দিচ্ছি
    seen_repos = set()
    first_check = get_repos()
    for r in first_check:
        seen_repos.add(r['id'])

    while True:
        repos = get_repos()
        for repo in repos:
            r_id = repo['id']
            r_name = repo['name']
            
            if r_id not in seen_repos:
                # নতুন রিপো পাওয়া গেছে!
                print(f"New Repo: {r_name}")
                send_msg(f"🚨 New Tool Detected: {r_name}\nDownloading...")
                
                # ডাউনলোড লিংক তৈরি
                zip_url = f"https://api.github.com/repos/{USER_CONFIG['GITHUB_TARGET_USER']}/{r_name}/zipball"
                headers = {"Authorization": f"token {USER_CONFIG['MY_GITHUB_TOKEN']}"}
                
                # ফাইল ডাউনলোড
                r = requests.get(zip_url, headers=headers, stream=True)
                if r.status_code == 200:
                    fname = f"{r_name}.zip"
                    with open(fname, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                    
                    # টেলিগ্রামে পাঠানো
                    send_file(fname, f"📦 Name: {r_name}\n🔗 URL: {repo['html_url']}")
                    
                    # সার্ভার থেকে ফাইল ডিলিট (স্টোরেজ বাঁচাতে)
                    os.remove(fname)
                
                seen_repos.add(r_id)
        
        time.sleep(USER_CONFIG['CHECK_TIME'])

if __name__ == "__main__":
    main()
