#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import cgi
import cgitb
cgitb.enable()

import matplotlib as mpl # matplotlib library for plotting and visualization
mpl.use('Agg')
import io
import sys
import matplotlib.pylab as plt # matplotlib library for plotting and visualization
import numpy as np #numpy library for numerical manipulation, especially suited for data arrays

form = cgi.FieldStorage()
if "L" not in form or "Vo" not in form or "V1" not in form or "d" not in form:
	print("Content-Type: text/html")    # HTML is following
	print()                             # blank line, end of headers
	print("<H1>Error</H1>")
	print("Please fill in the required fields.")
else:
	print("Content-Type: image/png")    # HTML is following
	print()                             # blank line, end of headers

	# Reading the input variables from the user
	Vo = abs(float(form["Vo"].value))
	L =  abs(float(form["L"].value))
	V1 = abs(float(form["V1"].value))
	d =  abs(float(form["d"].value))

	val = np.sqrt(2.0*9.10938356e-31*1.60217662e-19)*1e-10/(1.05457180013e-34)
	# equal to sqrt(2m_e (kg)* (Joules/eV)* 1 (m/A)/hbar (in J.sec)

	# Defining functions that come from the energy expression
	def f0(E):
	    var = -np.sqrt(Vo-E)+np.sqrt(E)*np.tan(np.sqrt(E)*val*(d/2.0+L))
	    var = var/(np.sqrt(E)+np.sqrt(Vo-E)*np.tan(np.sqrt(E)*val*(d/2.0+L)))
	    return var

	def f1(E):
	    var = np.sqrt(V1-E)*np.tanh(d*np.sqrt(V1-E)*val/2.0)+np.sqrt(E)*np.tan(d*np.sqrt(E)*val/2.0)
	    var = var/(np.sqrt(E)-np.sqrt(V1-E)*np.tanh(d*np.sqrt(V1-E)*val/2.0)*np.tan(d*np.sqrt(E)*val/2.0))
	    return var

	def f2(E):
	    var = np.sqrt(E)+np.sqrt(Vo-E)*np.tan(np.sqrt(E)*val*(d/2.0+L))
	    var = var/(np.sqrt(E)*np.tan(np.sqrt(E)*val*(d/2.0+L))-np.sqrt(Vo-E))
	    return var

	def f3(E):
	    var = np.sqrt(E)*np.tanh(d*np.sqrt(V1-E)*val/2.0)-np.sqrt(V1-E)*np.tan(d*np.sqrt(E)*val/2.0)
	    var = var/(np.sqrt(V1-E)+np.sqrt(E)*np.tanh(d*np.sqrt(V1-E)*val/2.0)*np.tan(d*np.sqrt(E)*val/2.0))
	    return var

	# We want to find the values of E in which f_even and f_odd are zero
	f_even = lambda E : f0(E)-f1(E)
	f_odd = lambda E : f2(E)-f3(E)
	E_old = 0.0
	f_even_old = f_even(0.0)
	f_odd_old = f_odd(0.0)
	n_even = 1
	n_odd = 1
	E_vals = np.zeros(999)
	n = 1
	# Here we loop from E = 0 to E = Vo seeking roots
	for E in np.linspace(0.0, Vo, 200000):
	    f_even_now = f_even(E)
	    # If the difference is zero or if it changes sign then we might have passed through a root
	    if (f_even_now == 0.0 or f_even_now/f_even_old < 0.0):
	        # If the old values of f are not close to zero, this means we didn't pass through a root but
	        # through a discontinuity point
	        if (abs(f_even_now)<1.0 and abs(f_even_old)<1.0):
	            E_vals[n-1] = (E+E_old)/2.0
	            n += 1
	            n_even += 1
	    f_odd_now = f_odd(E)
	    # If the difference is zero or if it changes sign then we might have passed through a root
	    if (f_odd_now == 0.0 or f_odd_now/f_odd_old < 0.0) and (E>0.0):
	        # If the old values of f are not close to zero, this means we didn't pass through a root but
	        # through a discontinuity point
	        if (abs(f_odd_now)<1.0 and abs(f_odd_old)<1.0):
	            E_vals[n-1] = (E+E_old)/2.0
	            n += 1
	            n_odd += 1
	    E_old = E
	    f_even_old = f_even_now
	    f_odd_old = f_odd_now
	nstates = n-1

	# Generating the energy diagram
	fig, ax = plt.subplots(figsize=(8,14))
	ax.spines['right'].set_color('none')
	ax.yaxis.tick_left()
	ax.spines['bottom'].set_color('none')
	ax.axes.get_xaxis().set_visible(False)
	ax.spines['top'].set_color('none')
	ax.axis([0.0,20.0,0.0,1.1*Vo])
	ax.set_ylabel(r'$E_n$ (eV)')
	for n in range(1,nstates+1):
	    str1="$n = "+str(n)+r"$, $E_{"+str(n)+r"} = %.3f$ eV"%(E_vals[n-1])
	    if(n%2==1):
	        ax.text(0.5, E_vals[n-1]-0.005*Vo, str1, fontsize=16, color="#ff4d4d")
	        ax.hlines(E_vals[n-1], 7.2, 18.3, linewidth=1.8, linestyle='--', color="#ff4d4d")
	    else:
	        ax.text(18.5, E_vals[n-1]-0.005*Vo, str1, fontsize=16, color="#800000")
	        ax.hlines(E_vals[n-1], 7.2, 18.3, linewidth=1.8, linestyle='--', color="#800000")
	str1="$V_o = %.3f$ eV"%(Vo)
	#ax.text(18.5, Vo-0.01*Vo, str1, fontsize=16, color="blue")
	ax.text(10, Vo+0.01*Vo, str1, fontsize=16, color="blue")
	ax.hlines(Vo, 7.2, 18.3, linewidth=1.8, linestyle='-', color="blue")
	ax.hlines(0.0, 0.0, 20.0, linewidth=1.8, linestyle='-', color="black")
	plt.title("Energy Levels", fontsize=30)
	plt.show()

	# Show the plots on the screen once the code reaches this point
	buf = io.BytesIO()
	plt.savefig(buf, format='png')
	buf.seek(0)  # rewind the data
	sys.stdout.flush()
	sys.stdout.buffer.write(buf.getvalue())
