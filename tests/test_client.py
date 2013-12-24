# -*- coding: utf-8 -*-
# Open Source Initiative OSI - The MIT License (MIT):Licensing
#
# The MIT License (MIT)
# Copyright (c) 2012 DotCloud Inc (opensource@dotcloud.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import gevent
import zmq

import zerorpc

from nose.tools import assert_raises
from testutils import teardown, random_ipc_endpoint

def test_client_connect():
    endpoint = random_ipc_endpoint()

    class MySrv(zerorpc.Server):

        def lolita(self):
            return 42

    srv = MySrv()
    srv.bind(endpoint)
    gevent.spawn(srv.run)

    client = zerorpc.Client()
    client.connect(endpoint)

    assert client.lolita() == 42

def test_client_quick_connect():
    endpoint = random_ipc_endpoint()

    class MySrv(zerorpc.Server):

        def lolita(self):
            return 42

    srv = MySrv()
    srv.bind(endpoint)
    gevent.spawn(srv.run)

    client = zerorpc.Client(endpoint)

    assert client.lolita() == 42


def test_client_encrypt_connect():
    # TODO: could LostRemote be better? maybe raise a AuthError?
    endpoint = random_ipc_endpoint()

    class MySrv(object):
        def lolita(self):
            return 42

    server_public, server_secret = zmq.curve_keypair()
    srv = zerorpc.Server(MySrv(), curve_key=server_secret)
    srv.bind(endpoint)
    gevent.spawn(srv.run)

    client = zerorpc.Client(curve_key=server_public)
    client.connect(endpoint)

    assert client.lolita() == 42
    client.close()

    # no key
    client = zerorpc.Client(heartbeat=0.25)
    client.connect(endpoint)
    with assert_raises(zerorpc.LostRemote):
        client.lolita()
    client.close()

    # bad key
    bad_server_public, _ = zmq.curve_keypair()
    client = zerorpc.Client(heartbeat=0.25, curve_key=bad_server_public)
    client.connect(endpoint)
    with assert_raises(zerorpc.LostRemote):
        client.lolita()
    client.close()
