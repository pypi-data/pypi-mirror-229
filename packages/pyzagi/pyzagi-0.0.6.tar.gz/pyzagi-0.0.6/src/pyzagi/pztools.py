def createbody(name:str, structure:list[str], values:list[str]):	
	params = []
	for i in range(len(structure)):
		params.append({
          "xpath": structure[i],
          "value": values[i]
        },)

	return {name:params}