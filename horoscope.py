import re
from enum import Enum
import datetime
from pymort import MortXML

Sex = Enum("Sex", ["ALL", "MALE", "FEMALE"])

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

def getTableYear(table: MortXML):
    yearRE = re.compile(r"(?:20|19|18)\d\d")
    matches = dict() #matches ordered by priority

    nameMatch = yearRE.search(str(table.ContentClassification.TableName))
    if nameMatch:
        matches[nameMatch.group()] = 1
    
    referenceMatch = yearRE.search(str(table.ContentClassification.TableReference))
    if referenceMatch:
        if referenceMatch.group() in matches:
            matches[referenceMatch.group()] = matches[referenceMatch.group()] + 1
        else:
            matches[referenceMatch.group()] = 1
    
    descriptionMatch = yearRE.search(str(table.ContentClassification.TableDescription))
    if descriptionMatch:
        if descriptionMatch.group() in matches:
            matches[descriptionMatch.group()] = matches[descriptionMatch.group()] + 1
        else:
            matches[descriptionMatch.group()] = 1
    
    matchKeys = iter(matches.keys())
    highest = 0 
    consensus = 0 
    for key in matchKeys:
        if matches[key] > highest:
            consensus = key
    
    return int(consensus)

def getTableSex(table: MortXML):
    maleRE = re.compile(r"[^e]male", re.I)
    femaleRE = re.compile(r"female", re.I)
    description = str(table.ContentClassification.TableDescription)
    name = str(table.ContentClassification.TableName)
    
    if maleRE.search(name) or maleRE.search(description):
        return Sex.MALE
    if femaleRE.search(name) or femaleRE.search(description):
        return Sex.FEMALE
    return Sex.ALL


print("getting")
exampleXml = MortXML.from_id(3153)
exampleLifeTable = MortXML.from_id(2829)
print('mort metadata: ' + str(exampleXml.Tables[0].MetaData))
print('life metadata: ' + str(exampleLifeTable.Tables[0].MetaData))
print('content type: ' + exampleXml.ContentClassification.ContentType)
print('data for given age: ' + str(getYearMortality(20, exampleXml)))
print('chance to die in 80 years at 20: ' + str(getRangeMortality(1, exampleXml, 80)))
print('chance to die in 110 years at 20: ' + str(getRangeMortality(20, exampleXml, 100)))
print("fraction outlived by 10 year old: " + str(getYearOutlived(10, exampleLifeTable)))
print("fraction outlived by 15 year old: " + str(getYearOutlived(15, exampleLifeTable)))
print("fraction outlived by 89 year old: " + str(getYearOutlived(98, exampleLifeTable)))
print("lifetable year: " + str(getTableYear(exampleLifeTable)))
print("mort year: " + str(getTableYear(exampleXml)))
print("mort sex: " + str(getTableSex(exampleXml)))
print("lifetable sex: " + str(getTableSex(exampleLifeTable)))