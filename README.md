# Forwarder_RTP


```
                     +--------------------------+
                     |                          |
                     |                          |
                     |          Server          |
                     |                          |
                     +-----------+--------------+
                     |  port in  | port forward |
                     +-----^-----+-------+------+
                           |             |
              +------------+             +---------^---+
              |                                    |   |
              |                                    |   |
       +------+------+                          +--+---v------+
       |             |                          |             |
       |     NAT     |                          |     NAT     |
       |             |                          |             |
       +------^------+                          +--^---+------+
Send data     |                  Make tunnel       |   | Receive UDP
stream to UDP |                  through NAT to UDP|   | data stream
              |                                    |   |
       +------+------+                          +--+---v------+
       | RTP + H264  |                          | RTP + H264  |
       |             |                          |             |
       |Stream to UDP|                          |Stream to UDP|
       +-------------+                          +-------------+
```


Start for test:

1. Run forwarding UDP in server 
```
# usage: forward_rtp_udp.py [-h] -a IP [-p PORT_IN] [-o PORT_FORWARD]
# PORT_IN, default = 64154
# PORT_FORWARD, default = 64155 

python3 forward_rtp_udp.py -a [IP of server] 
```
2. Run RTP client
```
# usage: rtp_client.py [-h] -a IP [-p PORT]
# PORT, default 64155

python3 rtp_client.py -a [IP of server]
```

3. Run RTP H264 streaming
```
gst-launch-1.0 -v videotestsrc ! video/x-raw,width=800, height=600, framerate=20/1 ! videoscale ! videoconvert ! x264enc tune=zerolatency bitrate=2048 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! udpsink host=[IP of server] port=64154
```