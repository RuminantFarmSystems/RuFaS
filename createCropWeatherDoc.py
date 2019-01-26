# This was just used to generate Inputs/crop_module_testWeather_3.4.csv so the
# results can match those in adjusted_model_PlantGrowth_3.5.xlsx
import openpyxl

inputWorkBook = openpyxl.load_workbook("others/__model_PlantGrowth_3.4.xlsx")

weatherSheet = inputWorkBook["Weather"]

def isEmpty(cell):
	return str(cell.value) == "None"

def rearrange(row):
	newRow = []
	newRow.append(row[1])
	newRow.append(row[6])
	for c in row[2:5]:
		newRow.append(c)
	newRow.append("0")
	newRow.append(row[5])
	newRow.append("0")
	return newRow

limit = 2
with open("Inputs/crop_module_testWeather_3.4.csv","w") as outFile:
	for row in weatherSheet:
		if not isEmpty(row[0]):
			valueList = [str(x.value) for x in row]
			valueList = rearrange(valueList)
			
			try:
				valueList[4] = str(float(valueList[2])/2 + float(valueList[3])/2)
			except Exception:
				print (valueList[2])
				print (valueList[3])
				print(valueList)
			newRow = ",".join(valueList)
			outFile.write(newRow + "\n")
