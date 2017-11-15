# Loadbalancer
This repo has some simple scripts for

1) Generating let's encrypt for a preset list of subdomains (this will go away in January, when Let's Encrypt adds wildcards)
2) Reading out Ingress rules from Kubernetes, matching their corresponding cluster ips, and generating HAProxy rules


This is simplier than actually implementing an Ingress Controller. It must run on a node of the cluster, or at the very least
on a machine that has been made aware of the software network of a cluster.



