import os, sys, json, random, platform, time, re, pyproxify
#from scapy.all import *
import itertools
import threading
try:
    import bs4
except:
    print(f"/033[01;32mModule bs4 could not be found")
from ua_headers import ua

r = "\033[31m"
g = "\033[32m"
y = "\033[33m"
b = "\033[34m"
p = "\033[35m"
d = "\033[2;37m"
w = "\033[0m"

W = f"{w}\033[1;47m"
R = f"{w}\033[1;41m"
G = f"{w}\033[1;42m"
Y = f"{w}\033[1;43m"
B = f"{w}\033[1;44m"
space = " "

red = '\033[31m'
yellow = '\033[93m'
lgreen = '\033[92m'
clear = '\033[0m'
bold = '\033[01m'
cyan = '\033[96m'
version = "1.4.3"
referer_list = ["https://www.google.com/", "https://www.youtube.com/", "https://www.twitter.com/", "https://www.discord.com/", "https://www.tiktok.com/", "https://www.instagram.com/", "https://check-host.net/", "https://github.com", "https://gitlab.com", "https://he1zen.rf.gd"]

major = str(sys.version_info.major)
minor = str(sys.version_info.minor)
path = str(sys.exec_prefix+"/lib/python"+major+"."+minor+"/site-packages/iphack/")

global log
global anon
anon = "web"
log = False

class ip:
    def address(*ips:str):
        import requests
        headers = {
		'User-Agent' : ua.linux()
	}
        ipaddr = " ".join([str(m) for m in ips])
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        try:
            myip = requests.get("https://trackip.net/ip", headers=headers).text
        except:
            myip = requests.get("https://api64.ipify.org?format=text", headers=headers).text
        if ipaddr == myip:
            b = red+bold+"["+clear+"-"+red+bold+"]"+clear
            print(b, "error, you can't punch your IP, so there is a command: ip.my()")
            exit(4)
        try:
            ipdata_list = ['?api-key=6818a70bf0dcdbf1dd6bf89e62299740a49725ac65ff8e4056e3b343', '?api-key=7d9bf69a54c63b6f9274c6074b2f50aee46208d10a33533452add840', '?api-key=6453632fcabd2a4c2de4bb45ab35254594fd719e61d58bacde4429f0']
            ipdata = random.choice(ipdata_list)
            data1 = requests.get("https://api.ipdata.co/"+ipaddr+ipdata, headers=headers, timeout=10).json()
            data6 = requests.get("http://ip-api.com/json/"+ipaddr+"?fields=status,message,isp,org,as,reverse,mobile,proxy,hosting,query,district", headers=headers, timeout=10).json()
            data7 = requests.get("https://api.ipregistry.co/"+ipaddr+"?key=g54hjdzjnudhhsp4", headers=headers, timeout=10).json()
            try:
                he1zen = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/iphack.json", timeout=10).json()
                he1zen = he1zen[ipaddr]
            except:
                he1zen = "None"
            try:
                html = bs4.BeautifulSoup(requests.get("https://spur.us/context/"+ipaddr, headers={"User-Agent": ua.windows()}).text, features="lxml")
                title = str(html.title)
                title = title.replace("IP Context - Spur</title>", "")
                title = title.replace("<title>", "")
                title = title.replace("(", "")
                title = title.replace(")", "")
                title = title.replace(ipaddr, "")
            except:
                title = "None"
            a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
            r = lgreen+bold+"["+red+bold+"!"+lgreen+bold+"]"+clear
            print(a, "┌──────────[Geolocation]")
            print(a, "├ Status             :", data6['status'])
            print(a, "├ Victim             :", data1['ip'])
            print(a, "┼ Is eu              :", data7['location']['in_eu'])
            print(a, "├ Type               :", data7['type'])
            print(a, "├ City               :", data7['location']['city'])
            print(a, "├ Region             :", data7['location']['region']['name'])
            print(a, "├ Region code        :", data7['location']['region']['code'])
            print(a, "├ Country code       :", data7['location']['country']['code'])
            print(a, "├ Country name       :", data7['location']['country']['name'])
            print(a, "├ Country capital    :", data7['location']['country']['capital'])
            print(a, "├ Country area       :", data7['location']['country']['area'])
            print(a, "├ Country tld        :", data7['location']['country']['tld'])
            print(a, "├ Calling code       :", "+"+data7['location']['country']['calling_code'])
            print(a, "├ Zip code           :", data7['location']['postal'])
            print(a, "├ Latitude           :", data7['location']['latitude'])
            print(a, "├ Longitude          :", data7['location']['longitude'])
            print(a, "├ Population         :", data7['location']['country']['population'])
            print(a, "├ Population density :", data7['location']['country']['population_density'])
            print(a, "└ Language name      :", data7['location']['language']['name'])
            district = data6['district']
            if district == "":
                district = "None"
            print(" ")
            print(a, "┌──────────[Router/Time]")
            print(a, "├ Asn name           :", data7['connection']['asn'])
            try:
                print(a, "├ Org name           :", data1['asn']['name'])
            except:
                print(a, "├ Org name           :", data7['connection']['organization'])
            print(a, "┼ Reverse            :", data6['reverse'])
            print(a, "├ Hostname           :", data7['hostname'])
            print(a, "├ District           :", district)
            print(a, "├ Type               :", data7['connection']['type'])
            print(a, "├ Abbr               :", data1['time_zone']['abbr'])
            print(a, "├ Offset             :", data1['time_zone']['offset'])
            print(a, "├ Time Zone          :", data1['time_zone']['name'])
            try:
                print(a, "├ Wifi Type          :", data1['asn']['type'])
            except:
                print(a, "├ Wifi Type          : Unknown")
            print(a, "├ Connection Domain  :", data7['connection']['domain'])
            print(a, "├ Company Domain     :", data7['company']['domain'])
            print(a, "├ Ip route           :", data7['connection']['route'])
            print(a, "└ Is dst             :", data1['time_zone']['is_dst'])
            print(" ")
            print(a, "┌──────────[Security]")
            print(a, "├ Is tor             :", data7['security']['is_tor'])
            print(a, "├ Is vpn             :", data7['security']['is_vpn'])
            print(a, "┼ Is proxy           :", data7['security']['is_proxy'])
            print(a, "├ Is relay           :", data7['security']['is_relay'])
            print(a, "├ Is hosting         :", data6['hosting'])
            print(a, "├ Is datacenter      :", data1['threat']['is_datacenter'])
            print(a, "├ Is anonymous       :", data7['security']['is_anonymous'])
            print(a, "├ Is attacker        :", data7['security']['is_attacker'])
            print(a, "├ Is abuser          :", data7['security']['is_abuser'])
            print(a, "├ Is threat          :", data7['security']['is_threat'])
            print(a, "└ Is bogon           :", data1['threat']['is_bogon'])
            print(" ")
            mb = data7['carrier']['name']
            if mb == None:
                mobile = "False"
            else:
                mobile = "True"
            print(a, "┌──────────[Carrier]")
            print(a, "┼ Mobile internet    :", mobile)
            print(a, "├ Carrier name       :", data7['carrier']['name'])
            print(a, "├ Carrier mcc        :", data7['carrier']['mcc'])
            print(a, "└ Carrier mnc        :", data7['carrier']['mnc'])
            print(" ")
            tor = data7['security']['is_tor']
            vpn = data7['security']['is_vpn']
            proxy = data7['security']['is_proxy']
            anon = data7['security']['is_anonymous']
            cloud = data7['security']['is_cloud_provider']
            attacker = data7['security']['is_attacker']
            threat = data7['security']['is_threat']
            if tor == True or vpn == True or proxy == True or anon == True or cloud == True or attacker == True or threat == True:
                spur = "spur.us/context/"+ipaddr
            else:
                spur = " "
            print(a, "┌──────────[Other]")
            print(a, "┼ spur.us            : "+spur)
            print(a, "├ additional info    : "+str(title))
            print(a, "└ he1zen info        : "+he1zen)
        except KeyboardInterrupt:
            print('Quiting Utility! Bye Bye, Have a nice day!'+lgreen)
            sys.exit(0)
        except requests.exceptions.ConnectionError as e:
            print(red+"[-]"+" Please check your internet connection!"+clear)
    def my():
        import requests
        headers = {
                'User-Agent' : ua.linux()
        }
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
        try:
            get = requests.get("https://ipapi.co//json/", headers=headers).json()
            print(a, "┌──────────[My IP Address]")
            print(a, "├ Ip address : ", get['ip'])
            print(a, "├ Version    : ", get['version'])
            print(a, "├ Country    : ", get['country_name'])
            print(a, "├ Capital    : ", get['country_capital'])
            print(a, "├ Latitude   : ", get['latitude'])
            print(a, "├ Longitude  : ", get['longitude'])
            print(a, "├ Timezone   : ", get['timezone'])
            print(a, "├ Postal     : ", get['postal'])
            print(a, "├ Area       : ", get['country_area'])
            print(a, "├ City       : ", get['city'])
            print(a, "├ Asn name   : ", get['asn'])
            print(a, "└ Org name   : ", get['org'])
        except:
            get = requests.get("https://api64.ipify.org?format=text", headers=headers).text
            print(a, "┌──────────[My IP Address]")
            print(a, "└ Ip address : "+get)
        print(" ")
        print(a, "┌──────────[Sys Info]")
        print(a, "├ System     : ", platform.system())
        print(a, "├ Release    : ", platform.release())
        print(a, "├ Processor  : ", platform.processor())
        print(a, "├ Version    : ", platform.version())
        print(a, "└ Machine    : ", platform.machine())
    def domain(*link:str):
        import requests
        headers = {
                'User-Agent' : ua.linux()
        }
        ur = " ".join([str(m) for m in link])
        url = "http://" + ur
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        a = lgreen+bold+"["+clear+"+"+lgreen+bold+"]"+clear
        r01 = url.replace("https://", "http://")
        url = r01.replace("http://http://", "http://")
        res=requests.get(url, stream=True, headers=headers)
        ip=res.raw._original_response.fp.raw._sock.getpeername()[0]
        res2=url + " : " + str(ip)
        print(a, "┌──────────[Domain Ip]")
        print(a, "└ "+url[7:] + " : " + str(ip))
    def subdomains(*domain:str):
        import requests
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        file = path+"subdomains.txt"
        domain = " ".join([str(m) for m in domain])
        subdomains = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/subdomains.txt").text
        subdomains = subdomains.splitlines()
        headers={"User-Agent": ua.windows()}
        sub = True
        while sub:
            for subdomain in subdomains:
                try:
                    domain = domain.replace("https://", "")
                    domain = domain.replace("http://", "")
                    url = f"http://{subdomain}.{domain}"
                    requests.get(url, headers=headers)
                except requests.ConnectionError:
                    pass
                else:
                    print(f"{space}{B} DONE {w} Status: {g}valid{w} URL: {url}")
            sub = False
    def directory(*domain:str):
        import requests
        print(red+"""
██╗██████╗░██╗░░██╗░█████╗░░█████╗░██╗░░██╗
██║██╔══██╗██║░░██║██╔══██╗██╔══██╗██║░██╔╝
██║██████╔╝███████║███████║██║░░╚═╝█████═╝░
██║██╔═══╝░██╔══██║██╔══██║██║░░██╗██╔═██╗░
██║██║░░░░░██║░░██║██║░░██║╚█████╔╝██║░╚██╗
╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝"""+red)
        print(yellow+bold+"        Developer: Misha Korzhik "+clear)
        print(yellow+bold+"           Tool Version: "+version+" \n"+clear)
        file = path+"directories.txt"
        domain = " ".join([str(m) for m in domain])
        directories = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/directories.txt").text
        directories = directories.splitlines()
        headers={"User-Agent": ua.windows()}
        sub = True
        while sub:
            for directory in directories:
                try:
                    domain = domain.replace("https://", "")
                    domain = domain.replace("http://", "")
                    url = f"http://{domain}/{directory}"
                    code = requests.get(url, headers=headers)
                    code = code.status_code
                except requests.ConnectionError:
                    pass
                else:
                    if code == 200:
                        print(f"{space}{B} DONE {w} Status: {g}valid{w} URL: {url}")
            sub = False
    def telegram(data=False):
        import requests
        infinity = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
        socks_ip = infinity["socksip"]
        socks_port = infinity["socksport"]
        if data:
           get = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=150")
           done = False
           def animate():
               for c in itertools.cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]):
                   if done:
                       break
                   sys.stdout.write('\r\x1B[32mParsing proxy ' + c + '\x1B[37m\r')
                   sys.stdout.flush()
                   time.sleep(0.07)
           t = threading.Thread(target=animate)
           t.start()
           time.sleep(2)
           done = True
           print("Proxies http(s)")
           print(get.text)
        else:
           get = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=250")
           done = False
           def animate():
               for c in itertools.cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]):
                   if done:
                       break
                   sys.stdout.write('\r\x1B[32mParsing proxy ' + c + '\x1B[37m\r')
                   sys.stdout.flush()
                   time.sleep(0.07)
           t = threading.Thread(target=animate)
           t.start()
           time.sleep(2)
           done = True
           print("Proxies Socks5")
           print(socks_ip+":"+socks_port)
           print(get.text)
    def proxy(data=False):
        import requests
        if data:
           list = []
           proxy_list = pyproxify.fetch(count=7, google=True, https=True)
           for item in proxy_list:
               ip = item["ip"]
               port = item["port"]
               list.append(ip+":"+port)
           proxy_list = pyproxify.fetch(count=8, https=True)
           for item in proxy_list:
               ip = item["ip"]
               port = item["port"]
               list.append(ip+":"+port)
           return list
        else:
           done = False
           def animate():
               for c in itertools.cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]):
                   if done:
                       break
                   sys.stdout.write('\r\x1B[32mParsing proxy ' + c + '\x1B[37m')
                   sys.stdout.flush()
                   time.sleep(0.07)
               sys.stdout.write('\r')
           t = threading.Thread(target=animate)
           t.start()
           time.sleep(2)
           done = True
           proxy_list = pyproxify.fetch(count=3, google=True, https=True)
           for item in proxy_list:
               ip = item["ip"]
               port = item["port"]
               last = item["last_update"]
               anonymity = item["anonymity"]
               country = item["country"]
               c_name = country["name"]
               print("Ip         : "+ip)
               print("Port       : "+port)
               print("Https      : False")
               print("Google     : True")
               print("Country    : "+c_name)
               print("Checked    : "+last)
               print("Anonymity  : "+anonymity)
               print(" ")

class search:
    def ip(*text:str):
        import requests, socket
        find = " ".join([str(m) for m in text])
        find = find.replace("https://", "")
        find = find.replace("http://", "")
        find = find.replace("/", "")
        find = find.replace(" ", "")
        get = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
        ip = str(get["mailip"])
        port = int(get["mailport"])
        check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        check.connect((ip, port))
        find = str(find)
        check.sendall(bytes("get|domain,ip|info|"+find,'UTF-8'))
        try:
            check.settimeout(10)
            code = check.recv(4096)
            get = code.decode('utf-8')
            if get == "-":
                print("no results")
            else:
                get = get.replace(",", "/")
                print(get)
        except:
            print("no results")

class check:
    def proxy(ip, port):
        import requests
        proxies = {"http":"http://"+ip+":"+port}
        headers = {"User-Agent": ua.windows()}
        info = requests.get("https://ipapi.co/"+ip+"/json/", headers=headers).json()
        try:
            with requests.Session() as p:
                p.proxies.update(proxies)
                http = p.get("http://api.ipify.org", headers=headers, timeout=15).text
                print("Proxy    : Online")
        except:
            print("Proxy    : Offline")
        print("Asn      : "+info["asn"])
        print("Org      : "+info["org"])
        print("City     : "+info["city"])
        print("Country  : "+info["country_name"])
        print("Region   : "+info["region"])
        print("Network  : "+info["network"])
        print("Version  : "+info["version"])

class inquiry:
    def get(*args, **kwargs):
        if anon == "tor":
            if log:
                print("[1%] Connecting to pluggable")
                print("[4%] Importing tor client")
                print("[7%] Tor http(s) adapter")
            from torpy import TorClient
            from torpy.http import requests as torrequ
            from torpy.http.adapter import TorHttpAdapter
            if log:
                print("[10%] Starting Orbot")
                print("[25%] Starting the tor client")
            with TorClient() as tor:
                if log:
                    print("[35%] Getting the tor guard")
                with tor.get_guard() as guard:
                    if log:
                        print("[45%] Tor Http Adapter, guard 3")
                    adapter = TorHttpAdapter(guard, 3)
                    with torrequ.Session() as sess:
                        if log:
                            print("[55%] Getting requests session")
                            print("[75%] Getting fake IP address")
                        sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                        sess.mount('http://', adapter)
                        sess.mount('https://', adapter)
                        if log:
                            print("[90%] Requests get URL")
                        try:
                            with eventlet.Timeout(25) as time:
                                get = sess.get(*args, **kwargs)
                                if log:
                                    print("[100%] Success")
                                return get
                        except:
                             return '\033[91m403 Website refused to connect\x1B[37m'
        elif anon == "vpn":
            if log:
                 print("[3%] Starting VPN method")
            try:
                 if log:
                     print("[8%] Importing proxy list")
                     print("[25%] Proxy type http(s)")
                 proxy_list = pyproxify.fetch(count=1, https=True)
                 for item in proxy_list:
                     ip = item["ip"]
                     port = item["port"]
                     proxy = ip+":"+port
                 if log:
                     print("[40%] Listening json list")
                     print("[55%] Proxy list imported")
                     print("[70%] Proxy "+ip+":"+port)
                 proxies = {"http":"http://"+proxy, "https":"http://"+proxy}
                 import requests
                 with eventlet.Timeout(10) as timeo:
                     if log:
                         print("[80%] Getting fake IP address")
                     with requests.Session() as s:
                         s.proxies.update(proxies)
                         args = " ".join([str(m) for m in args])
                         url = args.replace("https", "http")
                         if log:
                             print("[90%] Requests get URL")
                         referer = random.choice(referer_list)
                         get = s.get(url, **kwargs, headers={"Referer": referer, "User-Agent": ua.windows()})
                         if log:
                             print("[100%] Success")
                         return get
            except:
                 try:
                     p = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
                     ip = p["socksip"]
                     port = p["socksport"]
                     proxy = ip+":"+port
                     if log:
                         print("[92%] Failed using other proxy")
                         print("[95%] Proxy: "+ip+":"+port)
                     proxies = {"http":"socks5://he1zen:he1zen@"+proxy, "https":"socks5://he1zen:he1zen@"+proxy}
                     with eventlet.Timeout(15) as timeoo:
                         with requests.Session() as ss:
                             ss.proxies.update(proxies)
                             referer = random.choice(referer_list)
                             get = ss.get(args, **kwargs, headers={"Referer": referer, "User-Agent": ua.windows()})
                             if log:
                                 print("[100%] Success")
                             return get
                 except:

                     return '\033[91m403 Website refused to connect\x1B[37m'
        elif anon == "web":
            try:
                import requests
                if log:
                    print("[15%] Using web method")
                url = " ".join([str(m) for m in args])
                apis = ["4126596c0e563916f96dcf86ec00c269", "da70cc3727c1de7822f28902916ceb81", "19f75e81ed33f56c6ef5c09f22bf87f0"]
                if log:
                    print("[30%] Connecting to web")
                    print("[65%] Processing to get")
                key = random.choice(apis)
                paste = "https://api.scraperapi.com?api_key="+key+"&url="+url
                if log:
                    print("[90%] Requests get URL")
                referer = random.choice(referer_list)
                get = requests.get(paste, headers={"Referer": referer, "User-Agent": ua.linux()})
                if log:
                    print("[100%] Success")
                return get
            except:
                code = get.status_code
                return '\033[91m'+code+'\x1B[37m'
    def post(*args, **kwargs):
        if anon == "tor" or anon == "web":
            if anon == "web":
               print("Web method not supported on POST, only for the GET method")
            if log:
                print("[1%] Connecting to pluggable")
                print("[4%] Importing tor client")
                print("[7%] Tor http(s) adapter")
            from torpy import TorClient
            from torpy.http import requests as torrequ
            from torpy.http.adapter import TorHttpAdapter
            if log:
                print("[10%] Starting Orbot")
                print("[25%] Starting the tor client")
            with TorClient() as tor:
                if log:
                    print("[35%] Getting the tor guard")
                with tor.get_guard() as guard:
                    if log:
                        print("[45%] Tor Http Adapter, guard 3")
                    adapter = TorHttpAdapter(guard, 3)
                    with torrequ.Session() as sess:
                        if log:
                            print("[55%] Getting requests session")
                            print("[75%] Getting fake IP address")
                        sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                        sess.mount('http://', adapter)
                        sess.mount('https://', adapter)
                        if log:
                            print("[90%] Requests post URL")
                        try:
                            post = sess.post(*args, **kwargs)
                            if log:
                                print("[100%] Success")
                            return post
                        except:
                             return '\033[91m403 Website refused to connect\x1B[37m'
        elif anon == "vpn":
            if log:
                 print("[3%] Starting VPN method")
            try:
                 if log:
                     print("[8%] Importing proxy list")
                     print("[25%] Proxy type http(s)")
                 proxy_list = pyproxify.fetch(count=1, https=True)
                 for item in proxy_list:
                     ip = item["ip"]
                     port = item["port"]
                     proxy = ip+":"+port
                 if log:
                     print("[40%] Listening json list")
                     print("[55%] Proxy list imported")
                     print("[70%] Proxy "+ip+":"+port)
                 proxies = {"http":"http://"+proxy, "https":"http://"+proxy}
                 import requests
                 if log:
                     print("[80%] Getting fake IP address")
                 with requests.Session() as s:
                     s.proxies.update(proxies)
                     args = " ".join([str(m) for m in args])
                     url = args.replace("https", "http")
                     if log:
                         print("[90%] Requests post URL")
                     post = s.post(url, **kwargs, headers={"User-Agent": ua.windows()})
                     if log:
                         print("[100%] Success")
                     return post
            except:
                 try:
                     p = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
                     ip = p["socksip"]
                     port = p["socksport"]
                     proxy = ip+":"+port
                     if log:
                         print("[92%] Failed using other proxy")
                         print("[95%] Proxy: "+ip+":"+port)
                     proxies = {"http":"socks5://he1zen:he1zen@"+proxy, "https":"socks5://he1zen:he1zen@"+proxy}
                     with requests.Session() as ss:
                         ss.proxies.update(proxies)
                         post = ss.post(args, **kwargs, headers={"User-Agent": ua.windows()})
                         if log:
                             print("[100%] Success")
                         return post
                 except:
                     return '\033[91m403 Website refused to connect\x1B[37m'
    def put(*args, **kwargs):
        if anon == "tor" or anon == "web":
            if anon == "web":
               print("Web method not supported on POST, only for the GET method")
            if log:
                print("[1%] Connecting to pluggable")
                print("[4%] Importing tor client")
                print("[7%] Tor http(s) adapter")
            from torpy import TorClient
            from torpy.http import requests as torrequ
            from torpy.http.adapter import TorHttpAdapter
            if log:
                print("[10%] Starting Orbot")
                print("[25%] Starting the tor client")
            with TorClient() as tor:
                if log:
                    print("[35%] Getting the tor guard")
                with tor.get_guard() as guard:
                    if log:
                        print("[45%] Tor Http Adapter, guard 3")
                    adapter = TorHttpAdapter(guard, 3)
                    with torrequ.Session() as sess:
                        if log:
                            print("[55%] Getting requests session")
                            print("[75%] Getting fake IP address")
                        sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                        sess.mount('http://', adapter)
                        sess.mount('https://', adapter)
                        if log:
                            print("[90%] Requests put URL")
                        try:
                            put = sess.put(*args, **kwargs)
                            if log:
                                print("[100%] Success")
                            return put
                        except:
                            return '\033[91m403 Website refused to connect\x1B[37m'
        elif anon == "vpn":
            if log:
                 print("[3%] Starting VPN method")
            try:
                 if log:
                     print("[8%] Importing proxy list")
                     print("[25%] Proxy type http(s)")
                 proxy_list = pyproxify.fetch(count=1, https=True)
                 for item in proxy_list:
                     ip = item["ip"]
                     port = item["port"]
                     proxy = ip+":"+port
                 if log:
                     print("[40%] Listening json list")
                     print("[55%] Proxy list imported")
                     print("[70%] Proxy "+ip+":"+port)
                 proxies = {"http":"http://"+proxy, "https":"http://"+proxy}
                 import requests
                 if log:
                     print("[80%] Getting fake IP address")
                 with requests.Session() as s:
                     s.proxies.update(proxies)
                     args = " ".join([str(m) for m in args])
                     url = args.replace("https", "http")
                     if log:
                         print("[90%] Requests put URL")
                     put = s.put(url, **kwargs, headers={"User-Agent": ua.windows()})
                     if log:
                         print("[100%] Success")
                     return put
            except:
                 try:
                     p = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
                     ip = p["socksip"]
                     port = p["socksport"]
                     proxy = ip+":"+port
                     if log:
                         print("[92%] Failed using other proxy")
                         print("[95%] Proxy: "+ip+":"+port)
                     proxies = {"http":"socks5://he1zen:he1zen@"+proxy, "https":"socks5://he1zen:he1zen@"+proxy}
                     with requests.Session() as ss:
                         ss.proxies.update(proxies)
                         put = ss.put(args, **kwargs, headers={"User-Agent": ua.windows()})
                         if log:
                             print("[100%] Success")
                         return put
                 except:
                     return '\033[91m403 Website refused to connect\x1B[37m'
    def delete(*args, **kwargs):
        if anon == "tor" or anon == "web":
            if anon == "web":
               print("Web method not supported on POST, only for the GET method")
            if log:
                print("[1%] Connecting to pluggable")
                print("[4%] Importing tor client")
                print("[7%] Tor http(s) adapter")
            from torpy import TorClient
            from torpy.http import requests as torrequ
            from torpy.http.adapter import TorHttpAdapter
            if log:
                print("[10%] Starting Orbot")
                print("[25%] Starting the tor client")
            with TorClient() as tor:
                if log:
                    print("[35%] Getting the tor guard")
                with tor.get_guard() as guard:
                    if log:
                        print("[45%] Tor Http Adapter, guard 3")
                    adapter = TorHttpAdapter(guard, 3)
                    with torrequ.Session() as sess:
                        if log:
                            print("[55%] Getting requests session")
                            print("[75%] Getting fake IP address")
                        sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                        sess.mount('http://', adapter)
                        sess.mount('https://', adapter)
                        if log:
                            print("[90%] Requests delete URL")
                        try:
                            delete = sess.delete(*args, **kwargs)
                            if log:
                                print("[100%] Success")
                            return delete
                        except:
                            return '\033[91m403 Website refused to connect\x1B[37m'
        elif anon == "vpn":
            if log:
                 print("[3%] Starting VPN method")
            try:
                 if log:
                     print("[8%] Importing proxy list")
                     print("[25%] Proxy type http(s)")
                 proxy_list = pyproxify.fetch(count=1, https=True)
                 for item in proxy_list:
                     ip = item["ip"]
                     port = item["port"]
                     proxy = ip+":"+port
                 if log:
                     print("[40%] Listening json list")
                     print("[55%] Proxy list imported")
                     print("[70%] Proxy "+ip+":"+port)
                 proxies = {"http":"http://"+proxy, "https":"http://"+proxy}
                 import requests
                 if log:
                     print("[80%] Getting fake IP address")
                 with requests.Session() as s:
                     s.proxies.update(proxies)
                     args = " ".join([str(m) for m in args])
                     url = args.replace("https", "http")
                     if log:
                         print("[90%] Requests delete URL")
                     delete = s.delete(url, **kwargs, headers={"User-Agent": ua.windows()})
                     if log:
                         print("[100%] Success")
                     return delete
            except:
                 try:
                     p = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
                     ip = p["socksip"]
                     port = p["socksport"]
                     proxy = ip+":"+port
                     if log:
                         print("[92%] Failed using other proxy")
                         print("[95%] Proxy: "+ip+":"+port)
                     proxies = {"http":"socks5://he1zen:he1zen@"+proxy, "https":"socks5://he1zen:he1zen@"+proxy}
                     with requests.Session() as ss:
                         ss.proxies.update(proxies)
                         delete = ss.delete(args, **kwargs, headers={"User-Agent": ua.windows()})
                         if log:
                             print("[100%] Success")
                         return delete
                 except:
                     return '\033[91m403 Website refused to connect\x1B[37m'
    def head(*args, **kwargs):
        if anon == "tor" or anon == "web":
            if anon == "web":
               print("Web method not supported on POST, only for the GET method")
            if log:
                print("[1%] Connecting to pluggable")
                print("[4%] Importing tor client")
                print("[7%] Tor http(s) adapter")
            from torpy import TorClient
            from torpy.http import requests as torrequ
            from torpy.http.adapter import TorHttpAdapter
            if log:
                print("[10%] Starting Orbot")
                print("[25%] Starting the tor client")
            with TorClient() as tor:
                if log:
                    print("[35%] Getting the tor guard")
                with tor.get_guard() as guard:
                    if log:
                        print("[45%] Tor Http Adapter, guard 3")
                    adapter = TorHttpAdapter(guard, 3)
                    with torrequ.Session() as sess:
                        if log:
                            print("[55%] Getting requests session")
                            print("[75%] Getting fake IP address")
                        sess.headers.update({'User-Agent': 'Mozilla/5.0'})
                        sess.mount('http://', adapter)
                        sess.mount('https://', adapter)
                        if log:
                            print("[90%] Requests head URL")
                        try:
                            head = sess.head(*args, **kwargs)
                            if log:
                                print("[100%] Success")
                            return head
                        except:
                             return '\033[91m403 Website refused to connect\x1B[37m'
        elif anon == "vpn":
            if log:
                 print("[3%] Starting VPN method")
            try:
                 if log:
                     print("[8%] Importing proxy list")
                     print("[25%] Proxy type http(s)")
                 proxy_list = pyproxify.fetch(count=1, https=True)
                 for item in proxy_list:
                     ip = item["ip"]
                     port = item["port"]
                     proxy = ip+":"+port
                 if log:
                     print("[40%] Listening json list")
                     print("[55%] Proxy list imported")
                     print("[70%] Proxy "+ip+":"+port)
                 proxies = {"http":"http://"+proxy, "https":"http://"+proxy}
                 import requests
                 if log:
                     print("[80%] Getting fake IP address")
                 with requests.Session() as s:
                     s.proxies.update(proxies)
                     args = " ".join([str(m) for m in args])
                     url = args.replace("https", "http")
                     if log:
                         print("[90%] Requests head URL")
                     head = s.head(url, **kwargs, headers={"User-Agent": ua.windows()})
                     if log:
                         print("[100%] Success")
                     return head
            except:
                 try:
                     p = requests.get("https://raw.githubusercontent.com/mishakorzik/mishakorzik.menu.io/master/%D0%A1%D0%B5%D1%80%D0%B2%D0%B5%D1%80/https.json").json()
                     ip = p["socksip"]
                     port = p["socksport"]
                     proxy = ip+":"+port
                     if log:
                         print("[92%] Failed using other proxy")
                         print("[95%] Proxy: "+ip+":"+port)
                     proxies = {"http":"socks5://he1zen:he1zen@"+proxy, "https":"socks5://he1zen:he1zen@"+proxy}
                     with requests.Session() as ss:
                         ss.proxies.update(proxies)
                         delete = ss.delete(args, **kwargs, headers={"User-Agent": ua.windows()})
                         if log:
                             print("[100%] Success")
                         return delete
                 except:
                     return '\033[91m403 Website refused to connect\x1B[37m'
    def debug():
       global log
       if log:
           log = False
       else:
           log = True
    def rechange(type="tor"):
       global anon
       if type == "vpn" or type == "Vpn" or type == "VPN":
           anon = "vpn"
           return "Using: vpn"
       elif type == "tor" or type == "TOR" or type == "Tor":
           anon = "tor"
           return "Using: tor"
       elif type == "web" or type == "WEB" or type == "Web":
           anon = "web"
           return "Using: web"
       else:
           anon = "tor"
           return "Unknown type: "+type+", default tor"
