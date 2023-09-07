# -*- coding: utf-8 -*-
"""
@File    : cert_openssl.py
@Date    : 2022-10-22
@Author  : Peng Shiyu
"""

import socket
import ssl

import OpenSSL

from domain_admin.utils.cert_util import cert_common, cert_consts


def get_cert_info(domain_with_port):
    """
    获取证书信息
    存在问题：没有指定主机ip，不一定能获取到正确的证书信息
    :param domain_with_port: str
    :return: dict
    """
    domain_info = cert_common.parse_domain_with_port(domain_with_port)
    domain = domain_info.get('domain')
    port = domain_info.get('port', cert_consts.SSL_DEFAULT_PORT)

    # 设置默认超时时间，以防查询时间过程
    socket.setdefaulttimeout(cert_consts.DEFAULT_SOCKET_TIMEOUT)

    server_cert = ssl.get_server_certificate((domain, port))
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, server_cert)
    subject = cert.get_subject()
    issuer = cert.get_issuer()

    return {
        'domain': domain_with_port,
        # 'ip': cert_common.get_domain_ip(domain),
        'subject': cert_common.short_name_convert({
            'countryName': subject.countryName,
            'commonName': subject.commonName,
            'stateOrProvinceName': subject.stateOrProvinceName,
            'localityName': subject.localityName,
            'organizationName': subject.organizationName,
            'organizationalUnitName': subject.organizationalUnitName,
            'emailAddress': subject.emailAddress,
        }),
        'issuer': cert_common.short_name_convert({
            'countryName': issuer.countryName,
            'commonName': issuer.commonName,
            'stateOrProvinceName': issuer.stateOrProvinceName,
            'localityName': issuer.localityName,
            'organizationName': issuer.organizationName,
            'organizationalUnitName': issuer.organizationalUnitName,
            'emailAddress': issuer.emailAddress,
        }),
        # 'version': cert.get_version(),
        # 'serial_number': cert['serialNumber'],
        'start_date': cert_common.parse_time(cert.get_notBefore().decode()),
        'expire_date': cert_common.parse_time(cert.get_notAfter().decode()),
    }


if __name__ == '__main__':
    # print(get_cert_info('www.baidu.com'))
    # support
    # print(get_cert_info('www.mysite.com'))
    print(get_cert_info('cdn-image-01.kaishuleyuan.com'))
