'''
parent proxy sometimes lost Cache-Control headers if origin response have two or more Cache-Control headers
'''

#  Licensed to the Apache Software Continueation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

Test.Summary = 'parent proxy sometimes lost Cache-Control headers if origin response have two or more Cache-Control headers'

# Needs Curl
Test.SkipUnless(
    Condition.HasProgram("curl", "curl needs to be installed on system for this test to work"),
)
Test.ContinueOnFail = True

# Define default ATS
ts = Test.MakeATSProcess("ts")
ts2 = Test.MakeATSProcess("ts2")
server = Test.MakeOriginServer("server",lookup_key="{%X-Update}{PATH}")

# Define test headers
request_header1 = {"headers":
  "GET /default HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header1 = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header1, response_header1)

request_header2 = {"headers":
  "GET /age HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header2 = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: s-maxage=5\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header2, response_header2)

request_header3 = {"headers":
  "GET /nocache HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header3 = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: no-cache\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header3, response_header3)

request_header4 = {"headers":
  "GET /nocache_and_age_1 HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header4 = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: no-cache, s-maxage=5\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header4, response_header4)

request_header5 = {"headers":
  "GET /nocache_and_age_2 HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header5 = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: no-cache\r\n" +
  "Cache-Control: s-maxage=5\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header5, response_header5)

request_header6 = {"headers":
  "GET /maxage HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header6 = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: max-age=5\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
 }
server.addResponse("sessionlog.json", request_header6, response_header6)

request_header6a = {"headers":
  "GET /maxage1 HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header6a = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: max-age=0\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header6a, response_header6a)

request_header6b = {"headers":
  "GET /maxage2 HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: no\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header6b = {"headers":
  "HTTP/1.1 200 OK\r\n" +
  "Content-Length: 4\r\n" +
  "Connection: close\r\n" +
  "Cache-Control: max-age=0\r\n" +
  "ETag: \"5ca41161-1a\"\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": "test"
}
server.addResponse("sessionlog.json", request_header6b, response_header6b)

request_header6c = {"headers":
  "GET /maxage2 HTTP/1.1\r\n" +
  "Host: www.example.com\r\n" +
  "X-Update: yes\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body" : "",
}
response_header6c = {"headers":
  "HTTP/1.1 304 Not Modified\r\n" +
  "Connection: close\r\n" +
  "ETag: \"5ca41161-1a\"\r\n" +
  "\r\n",
  "timestamp": "12345678",
  "body": None
}
server.addResponse("sessionlog.json", request_header6c, response_header6c)

###### ATS Configuration ######
# ATS Configuration ( child node )
ts.Disk.plugin_config.AddLine('xdebug.so')
ts.Disk.remap_config.AddLine(
    'map http://www.example.com http://origin.example.com'
)
ts.Disk.parent_config.AddLine(
   'dest_domain=. parent="127.0.0.1:{port}"'.format(port=ts2.Variables.port)
)
ts.Disk.records_config.update({
   'proxy.config.http.parent_proxy.self_detect' : 0,
   'proxy.config.http.no_dns_just_forward_to_parent' : 1,
   'proxy.config.http.insert_request_via_str' : 1,
   'proxy.config.http.insert_response_via_str' : 3,
   'proxy.config.http.request_via_str' : 'ApacheTrafficServerChild',
   'proxy.config.http.response_via_str' : 'ApacheTrafficServerChild',
   'proxy.config.http.cache.ims_on_client_no_cache' : 0,
   'proxy.config.cache.ram_cache.algorithm': 1,
   'proxy.config.cache.ram_cache.use_seen_filter': 1,
   'proxy.config.log.logging_enabled' : 3,
   'proxy.config.diags.debug.enabled': 1,
   'proxy.config.diags.debug.tags': 'http|dns',
   'proxy.config.diags.output.debug': 'L',
   'proxy.config.hostdb.host_file.path' : '/etc/hosts',
})

# ATS Configuration ( parent node )
ts2.Disk.plugin_config.AddLine('xdebug.so')
ts2.Disk.remap_config.AddLine(
    'map / http://127.0.0.1:{0}'.format(server.Variables.Port)
)
ts2.Disk.records_config.update({
   'proxy.config.http.insert_request_via_str' : 1,
   'proxy.config.http.insert_response_via_str' : 3,
   'proxy.config.http.request_via_str' : 'ApacheTrafficServerParent',
   'proxy.config.http.response_via_str' : 'ApacheTrafficServerParent',
   'proxy.config.http.cache.ims_on_client_no_cache' : 0,
   'proxy.config.cache.ram_cache.algorithm': 1,
   'proxy.config.cache.ram_cache.use_seen_filter': 1,
   'proxy.config.log.logging_enabled' : 3,
   'proxy.config.diags.debug.enabled': 1,
   'proxy.config.diags.debug.tags': 'http|dns',
   'proxy.config.diags.output.debug': 'L',
   'proxy.config.hostdb.host_file.path' : '/etc/hosts',
})

###### Test Run ######
# Test 1     : not included Cache-Control is cache miss
#   ApacheTrafficServerParent [uScMsSf pSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSf pSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is blank(=not recorded) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is blank(=not recorded) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(server)
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.StartBefore(Test.Processes.ts2)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/default'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/default_miss.gold"
tr.StillRunningAfter = ts2

# Test 2 - 1 : included Cache-Control "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSfWpSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/age'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/age_miss.gold"
tr.StillRunningAfter = ts2

# Test 2 - 2 : included Cache-Control "Cache-Control: s-maxage=5" ( 2nd ) is cache hit
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS], ApacheTrafficServerChild [uScHs f p eN:t cCHp s ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/age'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/age_hit.gold"
tr.StillRunningAfter = ts2

# Test 3     : included Cache-Control "Cache-Control: no-cache" is cache miss
#   ApacheTrafficServerParent [uScMsSf pSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSf pSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is blank(=not recorded) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is blank(=not recorded) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   Same as Test 1 - not included Cache-Control is cache miss
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/nocache'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nocache_miss.gold"
tr.StillRunningAfter = ts2

# Test 4 - 1 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 1st ) is cache miss
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSfWpSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   Same as Test 2 - 1 : included Cache-Control "Cache-Control: s-maxage=5" ( 1st ) is cache miss
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/nocache_and_age_1'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nocache_and_age_miss_firsttime.gold"
tr.StillRunningAfter = ts2

# Test 4 - 2 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 2nd ) and origin return 200 OK is cache hit
#   ApacheTrafficServerParent [uScSsSfUpSeN:t cCSp sS] , ApacheTrafficServerChild [uScSsSfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/nocache_and_age_1'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nocache_and_age_hit_secondtime.gold"
tr.StillRunningAfter = ts2

# Test 5 - 1 : included Cache-Control "Cache-Control: no-cache" and "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSfWpSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   NOTE: 2 Cache-Control lines are integrated into 1 Cache-Control line (It is a behavior of autest origin)
#
#   Same as Test 4 - 1 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 1st ) is cache miss
#   Same as Test 2 - 1 : included Cache-Control "Cache-Control: s-maxage=5" ( 1st ) is cache miss
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/nocache_and_age_2'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nocache_and_age_miss_firsttime.gold"
tr.StillRunningAfter = ts2

# Test 5 - 2 : included Cache-Control "Cache-Control: no-cache" and "Cache-Control: s-maxage=5" ( 2nd ) is cache hit
#   ApacheTrafficServerParent [uScSsSfUpSeN:t cCSp sS] , ApacheTrafficServerChild [uScSsSfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#   NOTE: 2 Cache-Control lines are integrated into 1 Cache-Control line (It is a behavior of autest origin)
#
#   Same as Test 4 - 2 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 2nd ) and origin return 200 OK is cache hit
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/nocache_and_age_2'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nocache_and_age_hit_secondtime.gold"
tr.StillRunningAfter = ts2

# Test 6 - 1 : included Cache-Control "Cache-Control: max-age: 5" ( 1st ) is cache miss
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSfWpSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   Same as Test 2 - 1 : included Cache-Control "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   Same as Test 4 - 1 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 1st ) is cache miss
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_miss.gold"
tr.StillRunningAfter = ts2

# Test 6 - 2 : included Cache-Control "Cache-Control: max-age: 5" ( 2nd ) is cache hit
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS], ApacheTrafficServerChild [uScHs f p eN:t cCHp s ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
#   Same as Test 2 - 2 : included Cache-Control "Cache-Control: s-maxage=5" ( 2nd ) is cache hit
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_hit.gold"
tr.StillRunningAfter = ts2

# Test 6 - 3 : included Cache-Control "Cache-Control: max-age: 0" ( 1st ) is cache miss
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSfWpSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   Same as Test 2 - 1 : included Cache-Control "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   Same as Test 4 - 1 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 1st ) is cache miss
#   Same as Test 5 - 1 : included Cache-Control "Cache-Control: no-cache" and "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   Same as Test 6 - 1 : included Cache-Control "Cache-Control: max-age: 5" ( 1st ) is cache miss
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage1'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_miss.gold"
tr.StillRunningAfter = ts2

# Test 6 - 4 : included Cache-Control "Cache-Control: max-age: 0" ( 2nd ) and expired is cache stale , and origin return 200 OK
#   ApacheTrafficServerParent [uScSsSfUpSeN:t cCSp sS] , ApacheTrafficServerChild [uScSsSfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage1'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_stale.gold"
tr.StillRunningAfter = ts2

# Test 6 - 5 : included Cache-Control "Cache-Control: max-age: 0" ( 3rd ) and expired is cache stale , and origin return 200 OK
#   ApacheTrafficServerParent [uScSsSfUpSeN:t cCSp sS] , ApacheTrafficServerChild [uScSsSfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   Same as Test 6 - 4 : included Cache-Control "Cache-Control: max-age: 0" ( 2nd ) and expired is cache stale , and origin return 200 OK
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage1'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_stale.gold"
tr.StillRunningAfter = ts2

# Test 6 - 6 : included Cache-Control "Cache-Control: max-age: 0" and included ETag ( 1st ) is cache miss
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS] , ApacheTrafficServerChild [uScMsSfWpSeN:t cCMpSs ]
#
#   ApacheTrafficServerParent : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#                               cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is M(cache miss, url not in cache) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
#
#   Same as Test 2 - 1 : included Cache-Control "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   Same as Test 4 - 1 : included Cache-Control "Cache-Control: no-cache, s-maxage=5" ( 1st ) is cache miss
#   Same as Test 5 - 1 : included Cache-Control "Cache-Control: no-cache" and "Cache-Control: s-maxage=5" ( 1st ) is cache miss
#   Same as Test 6 - 1 : included Cache-Control "Cache-Control: max-age: 5" ( 1st ) is cache miss
#   Same as Test 6 - 3 : included Cache-Control "Cache-Control: max-age: 0" ( 1st ) is cache miss
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage2'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_miss.gold"
tr.StillRunningAfter = ts2

# Test 6 - 7 : included Cache-Control "Cache-Control: max-age: 0" and included ETag ( 2nd ) and expired is cache stale , and origin return 200 OK
#   ApacheTrafficServerParent [uIcSsSfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScSsNfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is I(If Modified Since,IMS) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is N(not-modified) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: no" http://localhost:{port}/maxage2'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_stale2.gold"
tr.StillRunningAfter = ts2

# Test 6 - 8 : included Cache-Control "Cache-Control: max-age: 0" and included ETag ( 3rd ) and expired is cache stale , and origin return 304 Not Modified
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScSsNfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is I(If Modified Since,IMS) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is N(not-modified) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" -H "X-Update: yes" http://localhost:{port}/maxage2'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/maxage_stale3.gold"
tr.StillRunningAfter = ts2
