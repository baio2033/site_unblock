import os,sys,threading,socket


def proxy_thread(conn, client_addr):
  # get the request from browser
  request = conn.recv(MAX_DATA_RECV)

  flag = False
  # parse the first line
  first_line = request.split('\n')[0]

  #print "################################\n", request, "################################\n"
  http_method = ['GET', 'POST', 'HEAD', 'PUT', 'OPTION', 'DELETE']
  #met_idx = request.find("GET")
  for m in http_method:
  	met_idx = request.find(m)
  	if met_idx != -1:
  		method = request[met_idx:met_idx+len(m)]
  		print "[+] HTTP Method : ", method
  		flag = True

  
  # get url
  url = first_line.split(' ')[1]
  #print request  

  if (DEBUG):
    print "first_line : ", first_line    
    print "URL:", url
    print

  host = ''
  if (flag):
  	if url.find("://") != -1:
  		url = url[url.find("://")+3:]
  	if url.find("/") != -1:
  		url = url[:url.find("/")]
  	host = url
  	print "[+] Host: ", host
  	host_idx = request.find(host+"\r\n")
  	#print request[:host_idx + len(host+"\r\n")]

  	#fake_request = first_line + "\r\nHost: " + host + "\r\n"
  	#fake_request = "GET / HTTP/1.1\r\nHost: " + host
  	line2_idx = request.find("\n") + 1
  	#print "[+] from line 2\n", request[line2_idx:]
  	#path = "GET / HTTP/1.1\r\n"
  	#fake_request = path + request[line2_idx:host_idx] + "dummy.com" +request[host_idx+len(host):]
  	#fake_request = request[:host_idx] + "dummy.com" + request[host_idx+len(host):]
  	fake_request = "GET / HTTP/1.1\r\nHost: dummy.com\r\n\r\n"
  	fake_request += request
  	if(DEBUG):
	  	print "[+] request"
	  	print request
  	#print "[+] fake request"
  	#print fake_request
  		
  try:
    # create a socket to connect to the web server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, 80))
    s.send(fake_request)         # send request to webserver
    cnt = 0
    while 1:
      # receive data from web server
      #print "[+] ", cnt, "th response"
      data = s.recv(MAX_DATA_RECV)
      if (len(data) > 0):
        # send to browser
        if data.count('HTTP/1.1') > 1:
        	print "[+] response count : ",data.count('HTTP/1.1')
        	data = data[3:]
        idx = data.find('HTTP/1.1 200 OK')

        if idx != -1:
        	response = data[idx:]
        else:
        	if data.find('HTTP/1.1 404 Not Found') == -1:
        		response = data
        	else:
        		continue
        #print "[+] response"
        #print response
        conn.send(response)
      else:
        break
    s.close()
    conn.close()
  except socket.error, (value, message):
    if s:
      s.close()
    if conn:
      conn.close()
    print "Runtime Error:", message
    sys.exit(1)

#********* CONSTANT VARIABLES *********
BACKLOG = 50            # how many pending connections queue will hold
MAX_DATA_RECV = 4096    # max number of bytes we receive at once
DEBUG = False          # set to True to see the debug msgs

#********* MAIN PROGRAM ***************
def main():

  # check the length of command running
  if (len(sys.argv) < 2):
    print "usage: proxy <port>"
    return sys.stdout

  # host and port info.
  host = '127.0.0.1'               # blank for localhost
  port = int(sys.argv[1]) # port from argument

  try:
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # associate the socket to host and port
    s.bind((host, port))

    # listenning
    s.listen(BACKLOG)
    print "####################################################"
    print "[+] PROXY : {}, {}".format(host, port)
    print "####################################################"

  except socket.error, (value, message):
    if s:
        s.close()
    print "Could not open socket:", message
    sys.exit(1)

  # get the connection from client
  while 1:
    conn, client_addr = s.accept()
    #print '\n[+] Accepted connection from ',client_addr[0], client_addr[1]
    # create a thread to handle request
    t = threading.Thread(target=proxy_thread, args=(conn, client_addr))
    t.start()

  s.close()

if __name__ == '__main__':
  main()