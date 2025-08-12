#!/usr/bin/python3
import numpy as np
from pyqtgraph.Qt import QtWidgets, uic
import pyqtgraph as pg
from seabreeze.spectrometers import list_devices, Spectrometer
import seatease.spectrometers
from datetime import datetime

import paths

class SpectraViewer():

	def __init__(self, spec=None):
		if spec is None:
			dev = list_devices()[0]
			self.spec = Spectrometer(dev)
		else:
			self.spec = spec
		self.lmbd = self.spec.wavelengths()

		self.app = QtWidgets.QApplication([])
		self.ui = uic.loadUi("spectrum.ui")
		self.plot_live = pg.PlotCurveItem()
		self.pen = pg.mkPen(color='r')
		self.ui.plot_full.addItem(self.plot_live)
		self.ui.show()

		self.ui.plot_full.showGrid(x=True, y=True, alpha=1.0)
		self.ui.plot_full.setXRange(194, 910)
		self.ui.plot_full.setYRange(0, 65535)
		self.ui.integration.setMinimum(int(self.spec.integration_time_micros_limits[0]/1000))
		self.ui.integration.setMaximum(int(self.spec.integration_time_micros_limits[1]/1000))
		self.ui.integration.setValue(100)
		self.set_integration_cb()

		self.ui.integration.valueChanged.connect(self.set_integration_cb)

		self.reset_avg()

		self.timer = pg.QtCore.QTimer()
		self.timer.timeout.connect(self.acquire)
		self.timer.start(5)

		self.app.exec_()

	def reset_avg(self):
		self.n = 0
		self.spectra_avg = np.zeros_like(self.lmbd)

	def acquire(self):
		self.spectra_avg += self.spec.intensities()
		self.n += 1
		if self.n == self.ui.n_average.value():
			self.update_plot()
		elif self.n > self.ui.n_average.value():
			self.reset_avg()

	def save_spectrum(self, all=False):
		name = self.ui.savepath.text()
		if name == '':
			name = 'spectrum'
		if all:
			name = paths.return_folder(paths.today() + name) + "/" + name
		else:
			name = paths.today() + name
			self.ui.saveone_button.setChecked(False)
		np.save(name + "_" + datetime.today().strftime("%H%M%S_%f"), self.spectra_avg)

	def update_plot(self):
		self.spectra_avg /= self.ui.n_average.value()

		if self.ui.saveall_button.isChecked():
			self.save_spectrum(all=True)
		elif self.ui.saveone_button.isChecked():
			self.save_spectrum(all=False)
			self.ui.saveone_button.setChecked(False)

		self.plot_live.setData(x=self.lmbd, y=self.spectra_avg, pen=self.pen)
		self.reset_avg()

	def set_integration_cb(self):
		self.spec.integration_time_micros(int(self.ui.integration.value() * 1000))
		self.reset_avg()

if __name__ == "__main__":
    sviewer = SpectraViewer(seatease.spectrometers.Spectrometer.from_first_available())
