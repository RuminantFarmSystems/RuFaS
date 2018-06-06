import sys


def main():
    expectedFileName = sys.argv[1]
    resultFileName = sys.argv[2]

    expectedFile = open(expectedFileName, "r")
    resultFile = open(resultFileName, "r")

    line = 0

    passed = "PASSED"
    skipFirst = True
    for rowExpected, rowResult in zip(expectedFile, resultFile):
        if skipFirst:
            skipFirst = False
            continue

        cellsExpected = rowExpected.split(",")
        cellsResult = rowResult.split(",")
        line += 1

        for i in range(len(cellsExpected)):
            try:
                valueExpected = float(cellsExpected[i])
                valueResult = float(cellsResult[i])
            except Exception as e:
                print("error")

            if abs(valueExpected - valueResult) > .00015:
                passed = "FAILED"
                print("error on line %i col %i in csv"% (line, i+1))
                print("Expected : %f \nResult  :  %f" % (valueExpected, valueResult))

    print("%s %s %s\n" % (passed, expectedFileName, resultFileName))

    expectedFile.close()
    resultFile.close()



if __name__ == "__main__":
    main()