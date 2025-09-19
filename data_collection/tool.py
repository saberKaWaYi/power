import subprocess

def fc(idrac_ip,username,password):
    command="ipmitool -I lanplus -H "+idrac_ip+" -U "+username+" -P "+f"\'{password}\' "+"sensor | grep PSU"
    process=subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    a=[];b=0;c=0
    for line in process.stdout.strip().split("\n"):
        if "Vin" in line:
            a.append(eval(line.split("|")[1]))
        if "Pin" in line:
            c+=eval(line.split("|")[1])
    a=sum(a)/len(a);b=c/a
    return [[round(a,2),round(b,2),round(c,2)]]

if __name__=="__main__":
    print(fc("10.194.26.3","ADMIN","ADMIN@123"))