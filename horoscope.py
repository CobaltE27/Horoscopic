from pymort import MortXML

def getYearMortality(age: int, tableXml: MortXML):
    startingAge = tableXml.Tables[0].MetaData.AxisDefs[0].MinScaleValue
    ageIndex = age - startingAge
    return tableXml.Tables[0].Values["vals"][ageIndex]

def getDayMortality(age: int, tableXml: MortXML):
    return getYearMortality(age, tableXml) / 365.0

def getRangeMortality(age: int, tableXml: MortXML, years: int):
    maxTableAge = tableXml.Tables[0].MetaData.AxisDefs[0].MaxScaleValue
    if (age + years - 1 > maxTableAge):
        return 1.0
    survivalChance = 1.0 - getYearMortality(age, tableXml)
    for futureAge in range (age + 1, age + years - 1):
        survivalChance *= 1 - getYearMortality(futureAge, tableXml)
    return 1.0 - survivalChance

print("getting")
exampleXml = MortXML.from_id(3153)
print('keywords: ' + str(exampleXml.ContentClassification.KeyWords))
print('metadata: ' + str(exampleXml.Tables[0].MetaData))
print('content type: ' + exampleXml.ContentClassification.ContentType)
print('data for given age: ' + str(getYearMortality(20, exampleXml)))
print('chance to die in 20 years at 20: ' + str(getRangeMortality(20, exampleXml, 20)))
print('chance to die in 60 years at 20: ' + str(getRangeMortality(20, exampleXml, 60)))
print('chance to die in 80 years at 20: ' + str(getRangeMortality(20, exampleXml, 80)))