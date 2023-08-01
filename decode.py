import http.client

conn = http.client.HTTPConnection("path_to_your_api")

headers = { 'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2Rldi1udXNkNDNpeWdwc2p3cWxqLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiIwRXFSd3Nxa1FNM3R3Q2xzZGJJNk9uSWI4VlJOTGdSNkBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9hdXRoLXJlZyIsImlhdCI6MTY5MDkwMDAxOSwiZXhwIjoxNjkwOTg2NDE5LCJhenAiOiIwRXFSd3Nxa1FNM3R3Q2xzZGJJNk9uSWI4VlJOTGdSNiIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.pfvXzQ9wUSjAkci5wY201g-rTpFzE0IPsFDkMG38LoA" }

conn.request("GET", "/", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))