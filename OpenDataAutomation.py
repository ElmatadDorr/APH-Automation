import argparse
import base64
from Crypto.Cipher import AES
from Crypto import Random
import cx_Oracle as ora
import pymssql as mssql
import pandas as pd
import time
import xml.etree.ElementTree as et
from socrata.authorization import Authorization
from socrata import Socrata

class OpenDataSet:

    def __init__(self):
        self.connectionType = ""
        self.server = ""
        self.username = ""
        self.password = ""
        self.database = ""
        self.port = ""
        self.query = ""
        self.view = ""
        self.config = ""
    
    def getConnection(self):
        if self.connectionType == "MSSQL":
            return mssql.connect(server=self.server, user=self.username, password=self.password, database=self.database)
        if conntype == "ORACLE":
            dsn_tns = ora.makedsn(self.server, self.port, self.database)
            return ora.connect(self.username, self.password, dsn_tns)
        else:
            return "unknown"

def main(args):
    # Get the dataset name from the command line
    if args.DataSet != "":
        
        # Get the dataset info from the XML
        ods = getDatasetInfo(args.DataSet)
        # Create the connection to the database
        connection = ods.getConnection()
        # Create the dataframe
        df = pd.read_sql(ods.query, con=connection)
        # Close the database connection
        connection.close
        # Save the dataframe to a file
        writeFile(df, args.FileName)
        # Post the file to SCGC?
        if args.Upload == True:
            # Authenticate to the portal
            auth = Authorization('austin-aph.data.socrata.com', 'Your_Socrata_Username', 'Your_Socrata_Password')
            socrata = Socrata(auth)
            # Find the view for the dataset
            (ok, view) = socrata.views.lookup(ods.view)
            assert ok, view
            # Open the file
            with open(args.FileName, 'rb') as my_file:
                # Get the config file for the view
                (ok, job) = socrata.using_config(ods.config, view).csv(my_file)
                assert ok, job
                # Write out the progress of the job
                assert ok, job
                (ok, job) = job.wait_for_finish(progress = lambda job: print('Job progress:', job.attributes['status']))


def getDatasetInfo(dsname):
    # Get the Dataset Specs from the XML
    root = et.parse("OpenDataConnections.xml")
    elm = root.findall("dataset[@name='" + dsname + "']")[0]
    # Load the Dataset Specs into an object
    ods = OpenDataSet()
    ods.connectionType = elm.find("connection").attrib['type']
    ods.username = elm.find("connection/username").text if elm.find("connection/username").attrib["plaintext"] == "Y" else decryptValue(elm.find("connection/username").text)
    ods.password = elm.find("connection/password").text if elm.find("connection/password").attrib["plaintext"] == "Y" else decryptValue(elm.find("connection/password").text)
    ods.database = elm.find("connection/database").text
    ods.server = elm.find("connection/server").text
    ods.port = elm.find("connection/port").text if elm.find("connection/port") is not None else ""
    ods.query = elm.find("query").text
    ods.view = elm.find("scgc/view").text if elm.find("scgc/view") is not None else ""
    ods.config = elm.find("scgc/config").text if elm.find("scgc/config") is not None else ""
    return ods

# Write the DataFrame to an Excel
def writeFile(df, filename):
    df.to_csv(filename, index=False, encoding='utf-8')

# Decrypt the String Value
def decryptValue(val):
    key = b'doih21nond21oinf'
    val = base64.b64decode(val)
    cipher = AES.new(key, AES.MODE_EAX, b";#q\x98\xbeeV\x12\x16\xf4\x99\xc0\x05.'9")
    ciphertext = cipher.decrypt(val)
    return ciphertext.decode()

if __name__ == '__main__':
    # Get the commandline arguements
    parser = argparse.ArgumentParser();
    parser.add_argument("-ds", dest="DataSet", help="The name of the dataset.")
    parser.add_argument("-fn", dest="FileName", nargs='?', default=time.strftime('%Y%m%d%H%M%S')+".csv", help="The name of the export file.")
    parser.add_argument("-up", dest="Upload", action="store_true", help="Upload to SCGC?")
    args = parser.parse_args()
    main(args)
