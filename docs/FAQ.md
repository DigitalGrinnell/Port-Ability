# FAQ and Troubleshooting

### Port Conflicts

If you encounter a problem like `Cannot start service traefik: b'driver failed programming external connectivity on endpoint summittservices_traefik_1 (f87653416555d8feda30e6aa48f15612f6abb5515b339ed5472d963ffef127f8): Error starting userland proxy: Bind for 0.0.0.0:8080 failed: port is already allocated'`...

This can be corrected by eliminating the conflict with the port (8080 in this case).  To determine what's occupying each port use `sudo lsof -i -n -P | grep TCP` or `sudo lsof -iTCP -sTCP:LISTEN -n -P` in OSX.

In OSX port 8080 is typically assigned to Nginx or Apache and can be opened by closing the local/built-in Nginx or Apache client.  

  Apache: `sudo apachectl stop`  
  NGINX: `sudo nginx -s stop`
