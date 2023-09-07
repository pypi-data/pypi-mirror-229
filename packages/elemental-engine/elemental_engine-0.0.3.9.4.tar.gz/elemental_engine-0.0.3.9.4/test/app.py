from elemental_engine import Engine


class App(Engine):

	def __init__(self):
		super().__init__()
		self.initialize()


app = App()
