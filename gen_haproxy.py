import json
import subprocess

def get_data():
    return {
        "ingress": json.loads(
            bytes.decode(subprocess.run(
                ["kubectl", "get", "--output=json", "ing", "--all-namespaces"],
                stdout=subprocess.PIPE
            ).stdout)
        ),
        "service": json.loads(
            bytes.decode(subprocess.run(
                ["kubectl", "get", "--output=json", "svc", "--all-namespaces"],
                stdout=subprocess.PIPE
            ).stdout)
        )
    }

def ip_for(services, name, namespace):
    res = list(map(
        lambda i: i["spec"]["clusterIP"],
        filter(
            lambda i: i["metadata"]["namespace"] == namespace and i["metadata"]["name"] == name,
            services
        )
    ))
    return res[0] if res else None

def get_items(data):
    res = []
    for i in data["ingress"]["items"]:
        be = i["spec"]["backend"]
        md = i["metadata"]
        name = md["name"]
        namespace = md["namespace"]
        url = "{}.{}".format(name, namespace.replace("-", "."))
        res.append({
            "url": url,
            "ip": ip_for(data["service"]["items"], be["serviceName"], namespace),
            "port": be["servicePort"]
        })
    return res

def certs_for(items):
    res = []
    for i in items:
        res.append("/etc/haproxy/certs/{}.pem".format(".".join(i["url"].split('.')[-2:])))
    return " crt".join(set(res))


def acls_for(items):
    res = []
    for i in items:
        res.append("acl host_{} hdr(host) -i {}".format(i["url"].replace(".", "_"), i["url"]))

    return "\n    ".join(res)

def use_acls_for(items):
    res = []
    for i in items:
        res.append("use_backend {} if host_{}".format(i["url"].replace(".", "_"), i["url"].replace(".", "_")))

    return "\n    ".join(res)

def backend_for(items):
    res = []
    for i in items:
        bname = i["url"].replace(".", "_")
        res.append("backend {}\n    mode http\n    server bk {}:{}".format(bname, i["ip"], i["port"]))

    return "\n".join(res)


def generate():
    data = get_data()
    items = get_items(data)
    return \
"""
global
    log /dev/log    local0
    log /dev/log    local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

    # Default SSL material locations
    ca-base /etc/ssl/certs
    crt-base /etc/ssl/private

    # Default ciphers to use on SSL-enabled listening sockets.
    # For more information, see ciphers(1SSL). This list is from:
    #  https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
    ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS
    ssl-default-bind-options no-sslv3

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

frontend gubi
    mode http
    bind :80
    redirect scheme https code 301

frontend https-in
    bind *:443 ssl crt {0}
    mode http
    {1}
    {2}
    #default_backend racetracks

{3}

""".format(
    certs_for(items),
    acls_for(items),
    use_acls_for(items),
    backend_for(items)
)

if(__name__ == "__main__"):
    print(generate())