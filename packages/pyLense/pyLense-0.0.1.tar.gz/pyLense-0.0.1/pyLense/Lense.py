
class Neurals:
	def __init__(self,link:str):
		self.link = link.strip()

	def check(self):
		if self.link.startswith("https://"):
			return "Yes"
		elif self.link.startswith("http://"):
			return "Yes"
		elif self.link.startswith("www."):
			return "Yes"
		else:
			return "Nah"
		
#creating the instance of a class
url = Neurals("")
#print(url.check())