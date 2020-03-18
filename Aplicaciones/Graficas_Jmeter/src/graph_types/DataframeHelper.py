from datetime import datetime
from itertools import repeat

def format_timestamp(timestamp):
    aux = datetime.fromtimestamp(timestamp//1000.0)
    return aux.strftime("%b_%a_%H.%M.%S")

def equilibrateListsWithNulls(mapKeyList, mapValueList):
    maxSize = 0
    referenceIndex = 0
    for index, (auxKey, auxValue) in enumerate(zip(mapKeyList,mapValueList)):
        maxSize = (maxSize,len(auxKey))[maxSize < len(auxKey)]
        referenceIndex = index
    print("El dataframe referencia está en la posición "+str(index)+" con "+str(maxSize)+" número de registros")
    referenceMapKey = mapKeyList[index]
    referenceMapValue = mapValueList[index]
    mapKeyList = [j for i, j in enumerate(mapKeyList) if i not in [index]]
    mapValueList = [j for i, j in enumerate(mapValueList) if i not in [index]]

    newMapKeyList = [referenceMapKey]
    newMapValueList = []
    for mapKey, mapValue in zip(mapKeyList,mapValueList):
        newMapValue = list(repeat(0, maxSize))
        mapKey = mapKey.tolist()
        for index, key in enumerate(referenceMapKey):
            if(key in mapKey):
                valueIndex = mapKey.index(key)
                newMapValue[index] = mapValue[valueIndex]

        newMapKeyList.append(referenceMapKey)
        newMapValueList.append(newMapValue)
    newMapValueList.insert(referenceIndex,referenceMapValue)
    return newMapKeyList, newMapValueList