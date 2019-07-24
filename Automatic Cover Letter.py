from __future__ import print_function
from mailmerge import MailMerge
from datetime import date
import os.path
save_path = "c:/Users/ElmatadD/Desktop"

Cover_letter = MailMerge("Dorr Elmatad - Template Cover Letter.docx")
print(Cover_letter.get_merge_fields())

Company = input("Company Name? ")
Street = input("What is their address? ")
City = input("City, State, Zip ")
Job = input("What is the job title? ")
Main = input("List the main responsibility? ")
Main = Main.lower()

name_of_file = "Dorr Elmatad - " + Company + " Cover Letter.PDF"

Cover_letter.merge(
    Date = '{:%d-%b-%Y}'.format(date.today()),
    Company = Company,
    Street = Street,
    City = City,
    Job = Job,
    Main = Main)


Cover_letter.write('Dorr Elmatad - ' + Company + " Cover Letter.docx")
