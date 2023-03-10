brd_group = []
fp_group = []
for group in grouped:
	refs = ""
	for c in group:
		if len(refs) > 0:
			refs += ", "
		refs += c.getRef()
#    package = get_package(c.getFootprint())
	package = c.getFootprint()
	value = c.getValue()
	manufacturer = c.getField("Manufacturer")
	part_no = c.getField("Part Number") + c.getField("Part number")
	stage = c.getField("Production Stage")
	#row = {"Refs": refs, "Value": value, "Part No": part_no, "Stage": stage}
	row = [refs, value, part_no, stage]
	if stage == "Board":
		brd_group.append(row)
	elif stage == "Faceplate Assm":
		fp_group.append(row)
	else:
		brd_group.append(row)		

for x in brd_group:
	print(x)
for y in fp_group:
	print(y)
	
	

