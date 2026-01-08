
### central server
- configure signing keys
- configure trust service
- configure initial member class
- configure management service (require one security server for this)
- configure xroad user (adduser with roles)

### security server (for central server)
- import anchor config from central server
- configure xroad user (adduser with roles)
- configure signing keys and certs via acme
    - generate keys and issue certs
    - register and approve cert on central server
- create and enable the management service
    - create the service and match the subsystem name of the configured on central server
    - approve the client on central server
- copy wsdl address from central server management service
- update management service endpoints from central server management service
- allow self security server to access management service

### security server (provider/consumer)
- import anchor config from central server
- configure xroad user (adduser with roles)
- configure signing keys and certs via acme
    - generate keys and issue certs
    - register and approve cert on central server
- create and enable any services (provider)
    - create and configure any services
    - approve the security server membership on central server
    - allow any clients on any services

### rest interface
headers:
    x-road-client: [instance]/[classX]/[memberX]/[subSystemX]

url: [proto]//:[securityServer:[port]]/r1/[instance]/[classY]/[memberY]/[subSystemY]/[service]/*
