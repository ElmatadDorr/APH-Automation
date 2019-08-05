from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from itertools import tee
import simplejson
import urllib
import googlemaps
import pandas as pd
import time
from socrata.authorization import Authorization
from socrata import Socrata
import sys
import os
import Combine_Data_for_EVI
import webbrowser
from math import radians, cos, sin, asin, sqrt
from haversine import haversine

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
def print_vaccine() :
    print("the possible choices for vaccines are:\n")
    print(inven.VaccID.unique())
    print('')
    print("Please copy and paste the vaccine you want from the above list ")
    return
def print_location() :
    print("the possible choices for locations that have this vaccine are:\n")
    print(inven['Provider'].unique())
    return
def lastUpdatedPrint():
    modx = os.path.getmtime('Dated_Vaccines.csv')
    xmod = datetime.fromtimestamp(modx)
    print('The last time the data was updated was on: ')
    print(xmod.date())
    print('')
    return

#Connect to geolocator and declare the program's name as the identifier
geolocator = Nominatim(user_agent="Vaccine Inventory For Austin Public Health", timeout=3)

#API key for geocoding with Googlemaps
#Set the api Key and also connect to google maps using the key
#API_key = 'AIzaSyD6qBdC8ND1NG_-8MBnMc77ArFWhRbpMOE'#enter Google Maps API key
#gmaps = googlemaps.Client(key=API_key)

#import our data
inven = pd.read_csv('VaccineRequestDataFile.csv')
dir = pd.read_csv('Locations_for_EVI.csv')

#Print when data was last updated
lastUpdatedPrint()

#change vaccine ids to not contain dashes and also not contain asterisks cause these break our program
inven['VaccID'] = inven['Vaccine'].str.split(')').str[0] + ') ' + inven['VaccID']
inven['VaccID'] = inven['VaccID'].str.replace('*', '')

#Prompt for Adult or Child and split the data into either only data that equals Adult or Pediatric
AorP = input("Is this for an adult or child? Enter A or P \n")
AorP = AorP.upper()
if AorP == 'A':
    #checks if last letter of the ID is A or not and splits accordingly
    inven = inven[inven.VaccID.str[-1:] == 'A' ]
    print('Searching for Adult Vaccines...\n')
    time.sleep(2)
elif AorP == 'P':
    #checks if last letter of the ID is P or not and splits accordingly
    inven = inven[inven.VaccID.str[-1:] == 'P' ]
    print('Searching for Child Vaccines...\n')
    time.sleep(2)
else:
    #If you enter neither A or P it will break and exit
    print('you entered '+ AorP)
    print('please enter A or next time. the program will now exit.')
    time.sleep(4)
    quit()

#Prompt for vaccine and list all options and Remove the records that do not have the vaccine we want
print_vaccine()
vacc = input()
print('Parsing Results...')
inven = inven[inven.VaccID == vacc]

#Geocodes our adress into a more robust address and then changes it into lat / long
inven['Street Address'] = inven['Street Address'] + ', Texas'
inven['Address'] = ''
inven['Address'] = inven['Street Address'].apply(geolocator.geocode)

#extra code for geocoding address into a lat long variable
#inven['coord'] = inven['Address'].apply(lambda x: (x.latitude, x.longitude))
#Sleep to ensure the API is not overburdened
#time.sleep(1)

inven.pop('Unnamed: 0')

#Extra code for printing out possible locations that need it,
#Useful once we can determine distance between two coords
#sorted_facilites = dir['Facility Name'].unique()
#print("the possible choices for locations that can receive this vaccine are:\n")
#print(sorted_facilites)
#print('')
#print("Please copy and paste the location that needs the vaccine")
#Point_B = input()

print('')
inven.to_excel("Recommended Locations for " + vacc.lower() + ".xlsx")
print('Success! Check for a file named Recommended Locations for ' + vacc.lower() + '.xlsx in the same directory as this program')
auth = Authorization(
    'austin-aph.data.socrata.com',
    os.environ['MY_SOCRATA_USERNAME'],
    os.environ['MY_SOCRATA_PASSWORD']
)

socrata = Socrata(auth)

(ok, view) = socrata.views.lookup('iy7u-7emm')
assert ok, view

with open("Recommended Locations for " + vacc.lower() + ".xlsx", 'rb') as my_file:
    (ok, job) = socrata.using_config('Recommended Locations for ipol (ipv) 49281086010p_08-05-2019_de4b', view).xlsx(my_file)
    assert ok, job
    # These next 3 lines are optional - once the job is started from the previous line, the
    # script can exit; these next lines just block until the job completes
    assert ok, job
    (ok, job) = job.wait_for_finish(progress = lambda job: print('Job progress:', job.attributes['status']))

webbrowser.open('https://austin-aph.data.socrata.com/dataset/Reducing-Vaccine-Waste-Project/iy7u-7emm', new = 2)
webbrowser.open('https://austin-aph.data.socrata.com/dataset/Recommended-Locations/t59f-nt5t', new = 2)
