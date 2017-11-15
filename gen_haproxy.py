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
