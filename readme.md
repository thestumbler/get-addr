# Format South Korean Addresses

Properly format a Korean address using the 
official [Korean Post Office website](http://www.juso.go.kr/support/AddressMainSearch2.do)
Given an incomplete or imperfect address, 
this site searches for a match and displays all matches,
only one match if your input string was good enough.
The search string can be in English or Korean,
and the site serves up both the English and Korean
results in one call.  This is true for the Korean
language search page, too.

## Program usage

  `python3 get-addr.py some-addrs.txt > results.txt`

## Inputs

  * **some-addrs.txt**
    - contains the less-than-complete addresses which to search for.
    - these can be either in English or Korean
    - one search address per line

## Outputs

  * **results.json** _(3)_
    - can be viewed "cleanly" using this command: 
      (requires jq, the JSON command line processor) 
      `$ cat results.json | jq ''`

  * **stdout**  _(4)_
    - tab-separated file of the results


## Output fields

  * _searched_   the address being searched for
  * _howmany_    how many matches were returned  (1)
  * _zipcode_    zip code
  * _new_eng_    English address, new street number and name format (2)
  * _old_eng_    English address, old land lot and number format   
  * _new_kor_    Korean address, new street number and name format
  * _old_kor_    Korean address, old land lot and number format   
  * _latitude_   Building latitude (5)
  * _longitude_  Building longitude


## Notes

  (1) The script doesn't fetch multiple addresses which might be
  returned.  If a search address returns more than one match, the site
  results should be visited manually to select the correct one.

  (2) Usually the site returns address on one line of text. But some
  are two lines (potentialy more).  The JSON output shows them as
  multiple lines, but the TSV file joins them as one line, separated
  buy a forward slash character.

  (3) Generation of JSON output can be controlled by setting the flag:
        `make_json_file = True or False`

  (4) Debugging output can be controlled by settng the flag:
        `print_verbose = True or False`

  (5) Lat / Lon values are just approximate. The precise mapping from
  post office isn't clear.  It isn't a standard ECEF geodetic 
  reference such as WGS84.  Preliminary analysis of the data shows
  that it is asymmetrically scaled and uses 
  the [Paracel Islands](https://en.wikipedia.org/wiki/Paracel_Islands)
  in the South China Sea as a reference point. Further study is needed.


