import amy

while True:
	text = input('\x1b[32mbasic >\x1b[0m ')
	if text.strip() == "": continue
	result, error = amy.run('<stdin>', text)

	if error:
		print(error.as_string())
	elif result:
		if len(result.elements) == 1:
			print(repr(result.elements[0]))
		else:
			print(repr(result))