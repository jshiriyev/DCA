import numpy

from scipy.stats import linregress

from ._model import Model

class Optimize():

	def __init__(self,mode:str=None,exponent:float=None):
		"""Initializes Optimization with the decline option.

		Decline option is mode-exponent pair, where exponent defines the mode:

		exponent 	: Arps' decline-curve exponent (b)

			b = 0 		-> mode = 'Exponential'
			0 < b < 100	-> mode = 'Hyperbolic'
			b = 100		-> mode = 'Harmonic' 
		
		The class contains methods to optimize curve fitting based on different modes.
		"""
		self._mode,self._exponent = Model.get_option(mode=mode,exponent=exponent)

	@property
	def mode(self):
		return self._mode
	
	@property
	def exponent(self):
		return self._exponent

	def fit(self,days:numpy.ndarray,rates:numpy.ndarray,date0=None):
		"""Inversely calculates decline model based on input days and rates:
		
		days 		: measured days, array of floats
		rates 		: measured rates, array of floats

		Returns decline model with mode, exponent, and initial rate and decline.
		"""
		rate0,decline0 = self.minimize(days,rates)

		return Model(mode=self.mode,exponent=self.exponent,
			date0=date0,rate0=rate0,decline0=decline0)

	@property
	def minimize(self):
		"""Returns the method based on the class mode."""
		return getattr(self,f"{self.mode}")

	def Exponential(self,days:numpy.ndarray,rates:numpy.ndarray):
		"""Optimization based on exponential decline model."""

		days,rates = days[rates!=0],rates[rates!=0]

		try:
			sol = linregress(days,numpy.log(rates))
		except ValueError:
			return 0.,0.

		return numpy.exp(sol.intercept),-sol.slope

	def Hyperbolic(self,days:numpy.ndarray,rates:numpy.ndarray):
		"""Optimization based on hyperbolic decline model."""

		exponent = self.exponent/100.

		days,rates = days[rates!=0],rates[rates!=0]

		try:
			sol = linregress(days,numpy.power(1/rates,exponent))
		except ValueError:
			return 0.,0.

		return sol.intercept**(-1/exponent),sol.slope/sol.intercept/exponent

	def Harmonic(self,days:numpy.ndarray,rates:numpy.ndarray):
		"""Optimization based on harmonic decline model."""

		days,rates = days[rates!=0],rates[rates!=0]

		try:
			sol = linregress(days,1/rates)
		except ValueError:
			return 0.,0.

		return sol.intercept**(-1),sol.slope/sol.intercept