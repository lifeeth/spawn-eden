import csv
import copy
with open('volunteers.csv', 'wb') as csvfiles:
    writer = csv.writer(csvfiles, delimiter=',')
    baseline = ['34','','FirstName','MiddleName','LastName','2-Jan-1987','3','FirstName.LastName@exammple.com','1234567890','','16','01-Jan-2012','31-Dec-2012','dummy','230','BuildingName','StreetAddress','560062','State','','City','','','','240']
    for i in range(1000):
        templine = copy.deepcopy(baseline)
        templine[2] = str(i) + baseline[2]
        templine[7] = str(i) + baseline[7]
        writer.writerow(templine)
