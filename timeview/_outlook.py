from ._timeview import TimeView

class Outlook(TimeView):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	def get_leads(self,*args):
		"""Returns series of items for the given groupkeys."""
		return self.get(list(args)).astype("str").agg(" ".join,axis=1)

	def get_heads(self,*args,include=None,exclude=None):
		"""Returns the list of heads including the dtypes in include, excluding the
		dtypes in exclude and safely dropping heads in args."""

		dtypes = self._frame.select_dtypes(
			include = include,
			exclude = exclude,
			)

		heads = dtypes.columns

		for head in args:
			try:
				heads = heads.drop(head)
			except KeyError:
				pass

		return heads.tolist()

	def items(self,*args):
		"""Returns the list of items for the given column names."""
		return self.get_leads(*args).unique().tolist()

	@property
	def datetimes(self):
		"""Returns the list of column names with datetime format."""
		return self.get_heads(include=('datetime64',))

	@property
	def numbers(self):
		"""Returns the list of column names with number format."""
		return self.get_heads(include=('number',))
	
	@property
	def nominals(self):
		"""Returns the list of column names that are categorical by nature."""
		return self.get_heads(exclude=('number','datetime64'))

	def minors(self,*args):
		"""Return the list of column names with number format, excluding the columns of args."""
		return self.get_heads(*args,include=('number',))

	def view(self,*args):
		"""Returns a new frame with the given groupkey (merged args) in the first column,
		date in the second column, and number columns in the rest."""

		leads = self.get_leads(*args)

		if leads.empty:
			return TimeView()

		dhead = self.datehead

		frame = self.get([dhead,*self.numbers])

		if frame.empty:
			return TimeView()

		lhead = "_".join(args)

		frame.loc[:,(lhead,)] = leads

		group = frame.groupby([lhead,dhead])
		frame = group.sum(self.numbers)
		frame = frame.reset_index()

		return TimeView(frame)(lhead,dhead)