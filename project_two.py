# Ishaan Taylor
# EECS 325 - Computer Networks
# Project 2

#  generates data : hop count, RTT, geographical distance
#  creates csv with data metrics, from that csv I created graphs to show the relationships:
#  x-axis:  hops |  hops      |  RTT
#  y axis:  RTT  |  distance  |  distance
#  
#  csv data format that is generated::
#  host name,  IP address,  ttl,  FALSE_RTT,  realRTT,   distance in miles

#cnn.com  157.166.226.25  13  61.02108955 18.73   551.2847475
#yahoo.com   98.138.253.109  18  156.1059952 20.87   2145.01843
#reddit.com  96.6.122.26 13  116.4288521 27.22   553.9980208
#baidu.com   123.125.114.144 17  496.6518879 23.49   6701.018918
#amazon.com  72.21.194.212   7   41.59712791 23.93   3938.789942
#twitter.com 199.59.149.230  7   44.22593117 26.74   2156.748603
#venmo.com   174.129.0.85    16  47.57189751 28.69   281.750082
#google.com  74.125.228.72   10  63.03596497 33.09   2147.730132
#case.edu    129.22.104.136  16  61.91897392 62.49   10.34623457
#facebook.com    173.252.110.27  13  58.1870079  22.14   2152.997586

# disregard false RTT for data analysis


import sys, time, timeit, math, socket, struct, re, urllib2, decimal, csv


hosts = """cnn.com
yahoo.com
reddit.com
baidu.com
amazon.com
twitter.com
venmo.com
google.com
case.edu
facebook.com"""


# main method simply runs the program, gathers data, and outputs a csv file in the tuple's format
def main():
    htp = createlist(hosts)                     #  store values
    results = []
    rttResults = []
    for host in htp:                            #  storing host, hops
        results.append(find_ttl(host))
        print(host)
    for i in range(0,len(results)):
        results.append(find_ttl(host))
        rttResults.append((rtt(results[i]),))   #  make the value a tuple so i can concat
        print (results[0], rttResults[i])
    default_longlat = locationfromIP("")
    print(default_longlat)
    coordinates = []
    distances = []
    for i in range(0,len(htp)):
        name = htp[i]
        ip = socket.gethostbyname(name)
        print (name,ip)
        temp = locationfromIP(ip)
        coordinates.append(temp)
        temp2 = distance(default_longlat[1],default_longlat[0],temp[1],temp[0])
        distances.append((temp2,))
        print ("Distance:", "{0:.1f}".format(float(distances[i][0]), "miles"))
        print("")
    final = []
    for i in range(0,len(results)):
        final.append(results[i] + rttResults[i] + distances[i])
    createcsv(final)
 

# takes original string in utf-8
# returns list of strings separated by newlines
def createlist(s):
     return(s.splitlines())


# input:  <Longitude>-81.6053</Longitude>
# or
# input:  <Latitude>41.5074</Latitude>
# returns string longitude 
def parsel(string):
     first = 0
     last  = 0 
     for i in range(0,len(string)):
          if string[i] == '>':
               first = i+1
          if string[i] == '/':
               last = i-1
               break
     return string[first:last]


# returns longitude and latitude in tuple 
def locationparse(lines):
     for i in range(0,len(lines)):
          m = re.search('>.*<', lines[i])
          if m:
               tempstring = m.string
               if 'Longitude' in tempstring:
                    long = parsel(tempstring)
               if 'Latitude' in tempstring:
                    lat = parsel(tempstring)
     return (float(long),float(lat))
               

# gets location from original xml formatted utf-8 text
def getlocation(string):
     lines = createlist(string)
     location = locationparse(lines)
     return location


# free go ip python sending requests and getting xml, then parsing the xml
def locationfromIP(ip):
     r = urllib2.urlopen(("http://www.freegeoip.net/xml/" + ip)).read().decode("utf-8")
     return getlocation(r)


#converts coordinates to distance on a sphere 
# multiple by 3960 if miles, else if kilometers by 6373
def distance(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
                # for two locations in spherical coordinates 
                # (1,theta,phi) and (1,theta,phi)
                # cosine(arc length) = sin phi sin phi' cos(theta-theta') + cos phi cos phi'
                # distance = rho * arc length
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    return arc*3960


# input:: result tuple in the form of: (host_name, host_ip, ttl, last_rtt)
def rtt(result):
    port = 33434                                     
    print ("result: ", result)
    rtt = 0.0                                               #  initialize important values
    host_name = result[0]
    host_ip = result[1]
    ttl = result[2]

    udp = socket.getprotobyname("udp")                      #  set up sockets
    icmp = socket.getprotobyname("icmp")             
    timeout = struct.pack("ll", 3, 0)                
    r = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)        #  raw socket: receive ICMP messages
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)       #  raw socket to send UDP packets
    r.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)    #  timeout
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)                 #  initial TTL for the UDP packet

    send_time = time.time()                 #  record time packet was sent
    s.sendto("", (host_name, port))         #  sends UDP packet to host over port
    current_ip = None                          
    pckt = False                      
    att = 3
    data = ""
    while data != "":                   #  listener
        data, host = r.recvfrom(512)    #  take 512 bytes
    rtt = (time.time() - send_time)     #  in ms
    r.close()                        #  close sockets
    s.close()
    return "{0:.2f}".format(rtt*1000)




#  returns a tuple : (hostName, hostIP, ttl, false_rtt)
def find_ttl(hostName):
                                               # setting up important fields
    port = 33434 
    hostIP = socket.gethostbyname(hostName) 
    udp = socket.getprotobyname("udp") 
    icmp = socket.getprotobyname("icmp") 
    timeout = struct.pack("ll", 3, 0) 
    min = 1 
    max = 48
    rtt = 0 
    ttl = 16 
    finished = False
    lc = 0 
    ttl2 = 0

    while not finished:
            rec = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)      #  setting up raw sockets
            send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)   
            rec.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout) 
            send.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl) 
            startT = time.time()                                            #  start timer
            send.sendto("", (hostName, port)) 
            current_ip = None 
            pckt = False                                                    #  loop condition
            att = 3                                                         #  max 3 attempts
            while not pckt and att > 0:
                try:
                    iData, host = rec.recvfrom(512)                         #  512 bytes 
                    endT = time.time() 
                    rtt = (endT - startT) * 1000                            #  end: round trip time
                    pckt = True
                    current_ip = host[0]
                    ipH = struct.unpack('!bBHHHBBH4s4s', iData[:20])        #  unpacked following IP header layout
                                                                            #  initialize IP header fields       
                    ihlv = ipH[0]
                    version = ihlv >> 4
                    ihL = ihlv & 0xF                                 
                    iphL = ihL * 4                                          #  IP header length
                    protocol = ipH[6]
                    source = socket.inet_ntoa(ipH[8])
                    destination = socket.inet_ntoa(ipH[9])                
                    icmpHeaderLength = 8                                    #  ICMP header length      
                    icmpB = iData[iphL:iphL + icmpHeaderLength]      
                    icmpH = struct.unpack('!BBHHH', icmpB) 
                    icmpT = icmpH[0]
                    icmpC = icmpH[1]
                    hl = iphL + icmpHeaderLength 
                    icmpD = iData[hl:] 

                except socket.error:             
                    att -= 1

            send.close()                                #  close sockets
            rec.close()

            ttl2 = ttl                                  #  precaution
            if current_ip is None:                      #  binary search probing
                current_ip = "*"
                icmpT = 11
                icmpC = 0
            if icmpT == 3:                              #  greater than or equal to
                max = ttl
                ttl = int((min + ((max - min) / 2)))
            else:
                if current_ip == "*":
                    if lc == 11:
                        min = ttl2
                        max = ttl
                        ttl = int((min + ((max - min) / 2 )))
                    else:
                        max = ttl2
                        ttl = int((min + ((max - min) / 2 )))
                else:                                   #  less than
                    min = ttl
                    ttl = int((min + ((max - min) / 2 )))
            if ttl == ttl2:
                finished = True
    return (hostName, hostIP, ttl, rtt)


# from a list of tuples, creates simple csv of data
def createcsv(results):
    final = open("data.csv","w")
    writer = csv.writer(final, delimiter=',', quoting=csv.QUOTE_ALL)
    for result in results:
        writer.writerow(result)
    final.close()


# command line call
if __name__ == "__main__":
    main()