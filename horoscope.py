import re
import json
from enum import Enum
import datetime
from pymort import MortXML

Sex = Enum("Sex", ["ALL", "MALE", "FEMALE"])
thisYear = datetime.datetime.now().year

SERIALIZABLE_ENUMS = {
    'Sex': Sex
    # ...
}

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in SERIALIZABLE_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)

def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(SERIALIZABLE_ENUMS[name], member)
    else:
        return d
#enum encoding/decoding from https://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json/24482806#24482806

def GatherTablesOfType(contentType: str):
    contentType = contentType.casefold()
    misses = 0
    tables = dict()
    id = 1
    while(1):
    #for id in range (3100, 3500):
        print("trying " + str(id))
        if misses >= 5000: #probably no more tables
            break
        try:
            table = MortXML.from_id(id) #should throw exception if it doesn't exist
            misses = 0
            if table.ContentClassification.ContentType.casefold() == contentType:
                tables[id] = {"year": GetTableYear(table), "sex": GetTableSex(table)}
        except FileNotFoundError:
            misses += 1
        id += 1
    
    return tables

def GetYearMortality(age: int, tableXml: MortXML):
    startingAge = GetMinimumAge(tableXml)
    ageIndex = age - startingAge + 1 #data indecies start at 1
    return tableXml.Tables[0].Values["vals"][ageIndex]

def GetDayMortality(age: int, tableXml: MortXML):
    return GetYearMortality(age, tableXml) / 365.0

def GetRangeMortality(age: int, tableXml: MortXML, years: int):
    maxTableAge = GetMaximumAge(tableXml)
    if (age + years - 1 > maxTableAge): #age range exceeds table size, guaranteed death for now
        return 1.0
    
    survivalChance = 1.0 - GetYearMortality(age, tableXml)
    for futureAge in range (age + 1, age + years - 1):
        survivalChance *= 1 - GetYearMortality(futureAge, tableXml)
    
    return 1.0 - survivalChance

def GetYearOutlived(age: int, lifeTable: MortXML):
    maxTableAge = GetMaximumAge(lifeTable)
    startingAge = GetMinimumAge(lifeTable)
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

def GetMinimumAge(tableXml: MortXML):
    minAgeRE = r"[Mm]in(?:imum)? [Aa]ge\D*(\d\d\d?)" #standard way of listing in description
    description = str(tableXml.ContentClassification.TableDescription)
    match = re.search(minAgeRE, description)
    if match:
        return int(match.group(1))
    else:
        return tableXml.Tables[0].MetaData.AxisDefs[0].MinScaleValue #less reliable, so only use if description doesn't list it

def GetMaximumAge(tableXml: MortXML):
    maxAgeRE = r"[Mm]ax(?:imum)? [Aa]ge\D*(\d\d\d?)"
    description = str(tableXml.ContentClassification.TableDescription)
    match = re.search(maxAgeRE, description)
    if match:
        return int(match.group(1))
    else:
        return tableXml.Tables[0].MetaData.AxisDefs[0].MaxScaleValue #less reliable, so only use if description doesn't list it

def GetTableYear(table: MortXML):
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

def GetTableSex(table: MortXML):
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
with open("mortalities", 'w') as mortalityTables:
    mortalityTables.write(json.dumps(GatherTablesOfType("healthy lives mortality"), cls=EnumEncoder))

#print(json.dumps(GatherTablesOfType("healthy lives mortality"), cls=EnumEncoder))
print("mort type: " + str(exampleXml.ContentClassification.ContentType))
print('mort metadata: ' + str(exampleXml.Tables[0].MetaData))
print('life metadata: ' + str(exampleLifeTable.Tables[0].MetaData))
print('data for given age: ' + str(GetYearMortality(20, exampleXml)))
print('chance to die in 80 years at 20: ' + str(GetRangeMortality(1, exampleXml, 80)))
print('chance to die in 110 years at 20: ' + str(GetRangeMortality(20, exampleXml, 100)))
print("fraction outlived by 10 year old: " + str(GetYearOutlived(10, exampleLifeTable)))
print("fraction outlived by 15 year old: " + str(GetYearOutlived(15, exampleLifeTable)))
print("fraction outlived by 89 year old: " + str(GetYearOutlived(98, exampleLifeTable)))
print("lifetable year: " + str(GetTableYear(exampleLifeTable)))
print("mort year: " + str(GetTableYear(exampleXml)))
print("mort sex: " + str(GetTableSex(exampleXml)))
print("lifetable sex: " + str(GetTableSex(exampleLifeTable)))