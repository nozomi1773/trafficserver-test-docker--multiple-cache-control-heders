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
server = Test.MakeOriginServer("server")

# Define test headers
request_header1 = {"headers": "GET /default HTTP/1.1\r\nHost: www.example.com\r\n\r\n", "timestamp": "12345678", "body": ""}
response_header1 = {"headers": "HTTP/1.1 200 OK\r\nContent-Length: 4\r\nConnection: close\r\n\r\n", "timestamp": "12345678", "body": "test"}
server.addResponse("sessionlog.json", request_header1, response_header1)

###### ATS Configuration ######
# ATS Configuration ( child node )
ts.Disk.plugin_config.AddLine('xdebug.so')
ts.Disk.remap_config.AddLine(
    'map http://www.example.com http://origin.example.com'
)
ts.Disk.parent_config.AddLine(
   'dest_domain=origin.example.com parent="127.0.0.1:{port}"'.format(port=ts2.Variables.port)
)
ts.Disk.records_config.update({
   'proxy.config.http.parent_proxy.self_detect' : 0,
   'proxy.config.http.no_dns_just_forward_to_parent' : 1,
   'proxy.config.http.insert_request_via_str' : 1,
   'proxy.config.http.insert_response_via_str' : 3,
   'proxy.config.http.request_via_str' : 'ApacheTrafficServerChild',
   'proxy.config.http.response_via_str' : 'ApacheTrafficServerChild',
})

# ATS Configuration ( parent node )
ts2.Disk.plugin_config.AddLine('xdebug.so')
ts2.Disk.remap_config.AddLine(
    'map / http://127.0.0.1:{0}'.format(server.Variables.Port)
)
ts2.Disk.records_config.update({
   'proxy.config.http.request_via_str' : 'ApacheTrafficServerParent',
   'proxy.config.http.response_via_str' : 'ApacheTrafficServerParent',
})

###### Test Run ######
# Test 1 - 1 : not included Cache-Control ( 1st )
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(server)
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.StartBefore(Test.Processes.ts2)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/default'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/default_miss.gold"
tr.StillRunningAfter = ts2

# Test 1 - 2 : not included Cache-Control ( 2nd )
tr = Test.AddTestRun()
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 -H "x-debug: x-cache,via" -H "Host: www.example.com" http://localhost:{port}/default'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/default_miss.gold"
tr.StillRunningAfter = ts2

