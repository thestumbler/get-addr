# Properly format a Korean address using the 
# official Korean Post Office website 
#
# This one displays the results in English,
# input can be in Korean or English
# http://www.juso.go.kr/support/AddressMainSearch2.do
#
#
# Program usage:
#   $  python3 get-addr.py some-addrs.txt > results.txt
#
# INPUTS:
#
# some-addrs.txt
#   contains less-than-complete addresses which to search for
#   these can be either in English or Korean
#
# OUTPUTS:
#
# results.json (3)
#   can be viewed "cleanly" using this command:
#   (requires jq, the JSON command line processor) 
#   $ cat results.json | jq ''
#
# stdout (4)
#   tab-separated file of the results
#
# 
# OUTPUT FIELDS:
#
#   searched   the address being searched for
#   howmany    how many matches were returned  (1)
#   zipcode    zip code
#   new_eng    English address, new street number and name format (2)
#   old_eng    English address, old land lot and number format   
#   new_kor    Korean address, new street number and name format
#   old_kor    Korean address, old land lot and number format   
#   latitude   Building latitude
#   longitude  Building longitude
#
#   (1) The script doesn't fetch multiple addresses which might be
#   returned.  If a search address returns more than one match, the site
#   results should be visited manually to select the correct one.
#
#   (2) Usually the site returns address on one line of text. But some
#   are two lines (potentialy more).  The JSON output shows them as
#   multiple lines, but the TSV file joins them as one line, separated
#   buy a forward slash character.
#
#   (3) Generation of JSON output can be controlled by setting the flag:
#         make_json_file = True or False
#
#   (4) Debugging output can be controlled by settng the flag:
#         print_verbose = True or False

#print_verbose = True
print_verbose = False

#make_json_file = False
make_json_file = True

import time
import sys
import signal
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import csv
import json

LOGGER.setLevel(logging.WARNING)

def eprint(*args):
  sys.stderr.write(' '.join(map(str,args)) + '\n')

def myprint(*args, **kw):
  print(*args, sep="", **kw)

def get_lat_lon( polat, polon ):
  lat_scale = 33000.0
  lon_scale = 27380.0
  lat_offset = 16.8
  lon_offset = 112.91
  llat = (float(polat) / lat_scale) + lat_offset
  llon = (float(polon) / lon_scale) + lon_offset
  return llat, llon

# json data output file
if make_json_file == True:
  fjson = open("results.json", "w")

# = open and read a list of less-than-perfect addresses
addr_searched=[]
fname=sys.argv[1]
lineno=1
with open(fname) as f:
  reader=csv.reader(f,delimiter='\t')
  for address in reader:
    addr_searched.append(address[0])
    lineno += 1
f.close()
#print(lineno-1)
#print(len(addr_searched))

# == Search ==
url = "http://www.juso.go.kr/support/AddressMainSearch2.do"
# Set Firefox Headless mode as TRUE
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
iloop=0
for addr in addr_searched:
  driver.get(url)
  time.sleep(2)
  source = driver.page_source.encode("utf-8")
  searchfor = driver.find_element_by_css_selector("form input[name='searchKeyword']")
  button = driver.find_element_by_css_selector("form input[type='button']")
  # print( "typeof searchfor:\t", type(searchfor))
  # print( "searchfor:\t", searchfor )
  # print( "button:\t", button )
  # print( "keys to send:\t", t )
  searchfor.click()
  searchfor.send_keys(addr)
  searchfor.send_keys(Keys.ENTER)
  # button.click()
  time.sleep(2)
  source = driver.page_source.encode("utf-8")
# Test with local file:
# url = "sample.html"
# source = open(url).read().encode("utf-8")
#endtest
  soup = BeautifulSoup(source, "html.parser")
  # print( soup.prettify().encode('utf-8') )
  # How many addresses were returned?
  howmany = soup.find("div", class_="result").find("p").text.split(' ',1)[0].strip()
  answer = soup.find("section", class_="section-search")
  # print( answer )
  # Fixed information, regardless of new/old, Eng/Kor:
  zipcode = answer.find("span", class_="zipcode").text.strip()
  # coords = list(map(str.strip("'"), answer.find("a", class_="map mobileMap").get('onclick').split('(', 1)[1].split(')')[0].split(',')[0:3] ))
  coords = [string.strip("'") for string in answer.find("a", class_="map mobileMap").get('onclick').split('(', 1)[1].split(')')[0].split(',')[0:3] ]
  lat, lon = get_lat_lon( coords[2], coords[1] )

  # English addresses:
  addr_eng = answer.find_all("li", class_="row eng_info")
  addr_kor = answer.find_all("li", class_="row kor_info")
  new_eng = list(map(str.strip, addr_eng[0].find("div", class_="cell st roadName").text.strip().splitlines() ))
  old_eng = list(map(str.strip, addr_eng[1].find("div", class_="cell num landLot").text.strip().splitlines() ))
  new_kor = list(map(str.strip, addr_kor[0].find("div", class_="cell st roadName").text.strip().splitlines() ))
  old_kor = list(map(str.strip, addr_kor[1].find("div", class_="cell num landLot").text.strip().splitlines() ))

  eprint( "search_address:\t", addr )

  if print_verbose == True:
    myprint( "search_address:\t", addr )
    myprint( "howmany_results:\t", howmany )
    myprint( "zipcode:\t",zipcode )
    for i, a in enumerate(new_eng, start=1):
      myprint("new_eng-",i,":\t",a )
    for i, a in enumerate(old_eng, start=1):
      myprint("old_eng.",i,":\t",a )
    for i, a in enumerate(new_kor, start=1):
      myprint("new_kor-",i,":\t",a )
    for i, a in enumerate(old_kor, start=1):
      myprint("old_kor-",i,":\t",a )
    for i, c in enumerate(coords, start=1):
      myprint("coords-",i,":\t",c )
    myprint("longitude:\t", lon )
    myprint("latitude:\t", lat )

  # json file output
  if make_json_file == True:
    fjson.write( json.dumps({ \
      "searched" : addr, \
      "howmany" : howmany, \
      "zipcode" : zipcode, \
      "new_eng" : new_eng, \
      "old_eng" : old_eng, \
      "new_kor" : new_kor, \
      "old_kor" : old_kor, \
      "latitude" : lat, \
      "longitude" : lon, \
    }) )

  # tab separated goes to stdout
  print( addr, end='\t' )
  print( howmany, end='\t' )
  print( zipcode, end='\t' )
  print( " / ".join(new_eng), end='\t' )
  print( " / ".join(old_eng), end='\t' )
  print( " / ".join(new_kor), end='\t' )
  print( " / ".join(old_kor), end='\t' )
  print( lat, end='\t' )
  print( lon, end='\n' )

  iloop+=1
  sys.stdout.flush()

# close browser
driver.quit()     
if make_json_file == True:
  fjson.close()







