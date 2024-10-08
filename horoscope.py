import re
from pymort import MortXML

def getYearMortality(age: int, tableXml: MortXML):
    startingAge = getMinimumAge(tableXml)
    ageIndex = age - startingAge + 1 #data indecies start at 1
    return tableXml.Tables[0].Values["vals"][ageIndex]

def getDayMortality(age: int, tableXml: MortXML):
    return getYearMortality(age, tableXml) / 365.0

def getRangeMortality(age: int, tableXml: MortXML, years: int):
    maxTableAge = getMaximumAge(tableXml)
    if (age + years - 1 > maxTableAge): #age range exceeds table size, guaranteed death for now
        return 1.0
    
    survivalChance = 1.0 - getYearMortality(age, tableXml)
    for futureAge in range (age + 1, age + years - 1):
        survivalChance *= 1 - getYearMortality(futureAge, tableXml)
    
    return 1.0 - survivalChance

def getYearOutlived(age: int, lifeTable: MortXML):
    maxTableAge = getMaximumAge(lifeTable)
    startingAge = getMinimumAge(lifeTable)
    poolSize = lifeTable.Tables[0].Values["vals"][1]

    numAlive = 0
    if (age > maxTableAge):
        numAlive = lifeTable.Tables[0].Values["vals"][maxTableAge - startingAge + 1] #data indecies start at 1
    elif (age < startingAge):
        return 0.0
    else:
        ageIndex = (age - startingAge) + 1 #data indecies start at 1
        numAlive = lifeTable.Tables[0].Values["vals"][ageIndex]

    return (poolSize - numAlive) / poolSize #fraction of pool you've outlived

def getMinimumAge(tableXml: MortXML):
    minAgeRE = r"[Mm]in(?:imum)? [Aa]ge\D*(\d\d\d?)" #standard way of listing in description
    description = str(tableXml.ContentClassification.TableDescription)
    match = re.search(minAgeRE, description)
    if match:
        return int(match.group(1))
    else:
        return tableXml.Tables[0].MetaData.AxisDefs[0].MinScaleValue #less reliable, so only use if description doesn't list it

def getMaximumAge(tableXml: MortXML):
    maxAgeRE = r"[Mm]ax(?:imum)? [Aa]ge\D*(\d\d\d?)"
    description = str(tableXml.ContentClassification.TableDescription)
    match = re.search(maxAgeRE, description)
    if match:
        return int(match.group(1))
    else:
        return tableXml.Tables[0].MetaData.AxisDefs[0].MaxScaleValue #less reliable, so only use if description doesn't list it


print("getting")
exampleXml = MortXML.from_id(3153)
exampleLifeTable = MortXML.from_id(2829)
print('keywords: ' + str(exampleXml.ContentClassification.KeyWords))
print('mort metadata: ' + str(exampleXml.Tables[0].MetaData))
print('life metadata: ' + str(exampleLifeTable.Tables[0].MetaData))
print('life description: ' + str(exampleLifeTable.ContentClassification.TableDescription))
print('content type: ' + exampleXml.ContentClassification.ContentType)
print('data for given age: ' + str(getYearMortality(20, exampleXml)))
print('chance to die in 80 years at 20: ' + str(getRangeMortality(1, exampleXml, 80)))
print('chance to die in 110 years at 20: ' + str(getRangeMortality(20, exampleXml, 100)))
print("fraction outlived by 10 year old: " + str(getYearOutlived(10, exampleLifeTable)))
print("fraction outlived by 15 year old: " + str(getYearOutlived(15, exampleLifeTable)))
print("fraction outlived by 89 year old: " + str(getYearOutlived(98, exampleLifeTable)))