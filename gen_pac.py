#!/usr/bin/env python3
from urllib import request, error
import os
import ipaddress
import json


def read_file(fname):
    if not os.path.exists(fname):
        return None
    with open(fname) as f:
        return f.read()


def write_file(fname, data):
    with open(fname, "w") as f:
        f.write(data)


def line_reader(fname):
    with open(fname) as f:
        for line in f.readlines():
            line =line.replace("\n", "")
            yield line


def china_ip_iter(line_iter):
    for line in line_iter:
        if "|CN|ipv4|" not in line:
            continue
        # apnic|CN|ipv4|219.149.192.0|16384|20020321|allocated
        _, _, _, ip, size, _, _ = line.split("|")
        yield ip, size


def download_record(fname, force_download=False):
    URL = "http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"
    etag_fname = "last_etag.txt"
    etag = read_file(etag_fname)
    try:
        rqst = request.Request(URL)
        if (not force_download) and etag and len(etag) > 0:
            rqst.add_header("If-None-Match", etag)
        resp = request.urlopen(rqst)
        data = resp.read()
        text = data.decode("UTF-8")
        write_file(fname, text)
        etag = resp.info()["ETag"]
        write_file(etag_fname, etag)
        return fname
    except error.HTTPError as e:
        if e.code == 304:
            return fname
        else:
            raise

PAC_TMPL = """
var proxy = "__PROXY__";

var direct = 'DIRECT;';

var addressInfo = {{ADDRESS}};

var cache = {};

function inChina(host){
    for (var net in addressInfo) {
        var netmark = addressInfo[net]
        if(isInNet(dnsResolve(host), net, netmark)){
            return true;
        }
    }
    return false;
}

function FindProxyForURL(url, host) {
    if(cache.hasOwnProperty(host)){
        return cache[host];
    }
    if(inChina(host)){
        cache[host] = direct;
        return direct;
    }else{
        cache[host] = proxy;
        return proxy;
    }
}
"""


def main():
    fname_ip = "./ip_record.txt"
    fname_pac = "./pac.txt"
    fname_ip = download_record(fname_ip)
    line_iter = line_reader(fname_ip)
    host_count2subnet_mark_length = {}
    for i in range(1, 32):
        host_count2subnet_mark_length[2**i] = 32 - i

    address = {}
    for ip_text, size_text in china_ip_iter(line_iter):
        ip_start = ipaddress.IPv4Address(ip_text)
        netmask_len = host_count2subnet_mark_length[int(size_text)]
        interface = ipaddress.IPv4Interface("%s/%s" % (ip_start, netmask_len))
        ip_with_netmark = interface.with_netmask
        net, netmark = ip_with_netmark.split("/")
        address[net] = netmark

    address_json = json.dumps(address, indent=4)
    pac_content = PAC_TMPL.replace("{{ADDRESS}}", address_json)
    write_file(fname_pac, pac_content)


if __name__ == '__main__':
    main()
