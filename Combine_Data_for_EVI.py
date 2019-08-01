import pandas as pd
def combine():

        #Read in our CSVs
    locations = pd.read_csv("Locations_for_EVI.csv")
    inventory = pd.read_csv("Dated_Vaccines.csv")

    #Creating our dataset to our specifications
    locations_addresses = locations[['Facility Name','Provider PIN', 'Street Address ']]
    locations_addresses = locations_addresses.rename(columns={"Facility Name": "Facility", "Street Address ": "Street Address"})
    locations_addresses['Facility'] = locations_addresses['Facility'].str.upper()
    inventory['Provider'] = inventory['Provider'].str.upper()
    LocationsPlusInventory = inventory.merge(locations_addresses,left_on='PIN',right_on='Provider PIN',how='left')
    LocationsPlusInventory = LocationsPlusInventory.drop(columns="Facility")
    locations_addresses = locations_addresses['Facility'].str.upper()
    LocationsPlusInventory['Item Number'] = LocationsPlusInventory['Item Number'].str.replace('-','')
    LocationsPlusInventory = LocationsPlusInventory.rename(columns={"Item Number": "VaccID"})

    #Warning if there are blank cells
    print("WARNING BLANK CELLS:")
    print("check for data quality issue in VaccineRequestDataFile.xlsx")
    print(LocationsPlusInventory.isnull().sum())


    #Write final product and move to second script
    LocationsPlusInventory.to_csv("VaccineRequestDataFile.csv")
    LocationsPlusInventory.to_excel("VaccineRequestDataFile.xlsx")

if __name__ == "__main__":
    combine()



