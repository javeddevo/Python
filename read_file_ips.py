def valid_ip(n):
    s=n.split(".")
    if len(s)!=4:
        return False
    for i in s:
        if not i.isdigit():
            return False
        if int(i)<0 or int(i)>255:
            return False
    return True

ip_address=[]
with open("abc.txt","r") as file:
    for i in file:
        res=i.split()
        for j in res:
            ip=valid_ip(j)
            if ip:
                ip_address.append(j)
print(ip_address)


## counting the lines
with open("abc.txt","r") as file:
    c=0
    for i in file:
        c=c+1
    print(c)
