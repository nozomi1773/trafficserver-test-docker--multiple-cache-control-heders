'''
parent proxy sometimes lost Cache-Control headers if origin response have two or more Cache-Control headers
but autest origin's response , 2 Cache-Control line definitions are integrated into 1 Cache-Control line (It is a behavior of autest origin)
so on this tests , I changed origin to nginx and tried again.
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

Test.Summary = 'parent proxy sometimes lost Cache-Control headers if origin response have two or more Cache-Control headers (origin=nginx)'

# Needs Curl
Test.SkipUnless(
    Condition.HasProgram("curl", "curl needs to be installed on system for this test to work"),
)
Test.ContinueOnFail = True

# Define default ATS
ts = Test.MakeATSProcess("ts")
ts2 = Test.MakeATSProcess("ts2")

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
    'map / http://127.0.0.1/'
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
# Test 1     : included "Cache-Control: public" is cache miss
#   ApacheTrafficServerParent [uScMsSf pSeN:t cCMp sS], ApacheTrafficServerChild [uScMsSf pSeN:t cCMpSs ]
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
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.StartBefore(Test.Processes.ts2)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_a/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_default_miss.gold"
tr.StillRunningAfter = ts2

# Test 2 - 1 : included "Cache-Control: max-age=5" ( 1st ) is cache miss , but cache-fill is W
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
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_b/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_miss.gold"
tr.StillRunningAfter = ts2

# Test 2 - 2 : included "Cache-Control: max-age=5" ( 2nd ) is hit-fresh
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS], ApacheTrafficServerChild [uScHs f p eN:t cCHp s ]
#
#   ApacheTrafficServerParent : this via info is child's cache
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_b/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_hit.gold"
tr.StillRunningAfter = ts2

# Test 2 - 3 : included "Cache-Control: max-age=5" ( 3rd ) is hit-fresh
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS], ApacheTrafficServerChild [uScRs f p eN:t cCHp s ]
#
#   ApacheTrafficServerParent : this via info is child's cache
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is R(in cache, fresh RAM hit) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_b/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_hit2.gold"
tr.StillRunningAfter = ts2

# Test 3 - 1 : included "Cache-Control: max-age=5, public" ( 1st ) is cache miss , but cache-fill is W
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
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_c/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_miss.gold"
tr.StillRunningAfter = ts2

# Test 3 - 2 : included "Cache-Control: max-age=5, public" ( 2nd ) is hit-fresh
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS], ApacheTrafficServerChild [uScHs f p eN:t cCHp s ]
#
#   ApacheTrafficServerParent : this via info is child's cache
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_c/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_hit.gold"
tr.StillRunningAfter = ts2

# Test 3 - 3 : included "Cache-Control: max-age=5, public" ( 3rd ) is hit-fresh
#   ApacheTrafficServerParent [uScMsSfWpSeN:t cCMp sS], ApacheTrafficServerChild [uScRs f p eN:t cCHp s ]
#
#   ApacheTrafficServerParent : this via info is child's cache
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is R(in cache, fresh RAM hit) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_c/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_hit2.gold"
tr.StillRunningAfter = ts2

# Test 4 - 1 : included "Cache-Control: max-age=5, public, no-cache" ( 1st ) is cache miss , but cache-fill is W
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
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_d/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_miss.gold"
tr.StillRunningAfter = ts2

# Test 4 - 2 : included "Cache-Control: max-age=5, public, no-cache" ( 2nd ) is fresh-hit , but cache-fill is U
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScSsNfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is I(If Modified Since) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is N(not-modified) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_d/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_hit.gold"
tr.StillRunningAfter = ts2

# Test 4 - 3 : included "Cache-Control: max-age=5, public, no-cache" ( 3rd ) is fresh-hit , but cache-fill is U
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScSsNfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is I(If Modified Since) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is N(not-modified) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_d/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_hit.gold"
tr.StillRunningAfter = ts2

# Test 5 - 1 : included "Cache-Control: max-age=5, public" and "Cache-Control: no-cache" ( 1st ) is cache miss , but cache-fill is W
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
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_d/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_miss2.gold"
tr.StillRunningAfter = ts2

#####################################################################################################
# NOTE : in this pattern , lost Cache-Control headers 2nd line ("Cache-Control: no-cache")
#####################################################################################################
# Test 5 - 2 : included "Cache-Control: max-age=5, public" and "Cache-Control: no-cache" ( 2nd ) is is fresh-hit , but cache-fill is U
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScSsNfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is I(If Modified Since) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is N(not-modified) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_e/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_hit2.gold"
tr.StillRunningAfter = ts2

#####################################################################################################
# NOTE : in one before pattern , lost Cache-Control headers 2nd line ("Cache-Control: no-cache")
#        in this pattern , no-cache control is not working
#####################################################################################################
# Test 5 - 2 : included "Cache-Control: max-age=5, public" and "Cache-Control: no-cache" ( 2nd ) is is fresh-hit
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScHs f p eN:t cCHp s ])
#
#   ApacheTrafficServerParent : this via info is child's cache
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                                parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_e/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_hit3.gold"
tr.StillRunningAfter = ts2

#####################################################################################################
# NOTE : in two before pattern , lost Cache-Control headers 2nd line ("Cache-Control: no-cache")
#        in this pattern , no-cache control is not working
#####################################################################################################
# Test 5 - 3 : included "Cache-Control: max-age=5, public" and "Cache-Control: no-cache" ( 3rd ) is is fresh-hit
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScRs f p eN:t cCHp s ])
#
#   ApacheTrafficServerParent : this via info is child's cache
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is R(in cache, fresh RAM hit) , server-info is blank(no server connection needed) ,
#                               cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is H(cache hit) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_e/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_hit4.gold"
tr.StillRunningAfter = ts2

# Test 6 - 1 : included "Cache-Control: no-cache" and "Cache-Control: max-age=5, public" ( 1st ) is cache miss , but cache-fill is W
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
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_f/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_miss3.gold"
tr.StillRunningAfter = ts2

#####################################################################################################
# NOTE : in one before pattern , lost Cache-Control headers 2nd line ("Cache-Control: max-age=5, public")
#        in this pattern , max-age=5 is not working
#####################################################################################################
# Test 6 - 2 : included "Cache-Control: no-cache" and "Cache-Control: max-age=5, public" ( 2nd ) is fresh-hit , but cache-fill is U
#   ApacheTrafficServerParent [uIcSsNfUpNeN:t cCSp sS] , ApacheTrafficServerChild [uScSsNfUpSeN:t cCSpSs ]
#
#   ApacheTrafficServerParent : client-info is I(If Modified Since) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is N(not-modified) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is blank(no parent proxy) , server-conn-info is S(connection opened successfully)
#
#   ApacheTrafficServerChild  : client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is N(not-modified) ,
#                               cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error) ,
#                               tunnel-info is blank(no tunneling) , cache-type is C(cache) and cache-lookup-result is S(cache hit, but expired) ,
#                               parent-proxy is S(connection opened successfully) , server-conn-info is blank(no server connection)
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/test_f/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/nginx_age_public_nocache_hit5.gold"
tr.StillRunningAfter = ts2





