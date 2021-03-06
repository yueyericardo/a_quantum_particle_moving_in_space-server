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

	# Drawing the backgroung graph
	fig, axes = plt.subplots(1, 2, figsize=(19,9))
	axes[0].spines['right'].set_color('none')
	axes[0].xaxis.tick_bottom()
	axes[0].spines['left'].set_color('none')
	axes[0].axes.get_yaxis().set_visible(False)
	axes[0].spines['top'].set_color('none')

	if (V1 > 1.4*Vo):
	    Ymax=1.4*Vo
	else:
	    Ymax=1.1*V1
	axes[0].axis([-1.5*L-d/2.0,1.5*L+d/2.0,0.0,Ymax])
	axes[0].set_xlabel(r'$X$ (Angstroms)')
	str1="$V_o = %.2f$ eV"%(Vo)
	str2="$V_1 = %.2f$ eV"%(V1)
	axes[0].text(1.05*(L+d/2.0), 1.02*Vo, str1, fontsize=24, color="blue")
	axes[0].text(-1.5*(L+d/2.0), 1.02*Vo, str1, fontsize=24, color="blue")
	if(d>0.0): axes[0].text(d/2, 1.02*Vo, str2, fontsize=24, color="blue")
	# Defining the maximum amplitude of the wavefunction
	if ((E_vals[1]-E_vals[0])/(E_vals[2]-E_vals[0]) < 0.2):
	    amp = np.sqrt((E_vals[2]-E_vals[0])/1.5)
	else:
	    amp = np.sqrt((E_vals[1]-E_vals[0])/1.5)
	# Plotting the energy levels
	for n in range(1,nstates+1):
	    # Odd solution
	    if (n%2==0): axes[0].hlines(E_vals[n-1], -1.5*L-d/2.0, 1.5*L+d/2.0, linewidth=1.8, linestyle='--', color="#800000")
	    # Even solution
	    if (n%2==1): axes[0].hlines(E_vals[n-1], -1.5*L-d/2.0, 1.5*L+d/2.0, linewidth=1.8, linestyle='--', color="#ff4d4d")
	axes[0].margins(0.00)
	axes[0].vlines(-L-d/2.0, 0.0, Vo, linewidth=4.8, color="blue")
	if(d>0.0):
	    axes[0].vlines(-d/2.0, 0.0, V1, linewidth=4.8, color="blue")
	    axes[0].vlines(d/2.0, 0.0, V1, linewidth=4.8, color="blue")
	axes[0].vlines(L+d/2.0, 0.0, Vo, linewidth=4.8, color="blue")
	axes[0].hlines(Vo, -1.5*L-d/2.0, -L-d/2.0, linewidth=4.8, color="blue")
	axes[0].hlines(0.0, -L-d/2.0, -d/2.0, linewidth=4.8, color="blue")
	axes[0].hlines(V1, -d/2.0, d/2.0, linewidth=4.8, color="blue")
	axes[0].hlines(0.0, d/2.0, L+d/2.0, linewidth=4.8, color="blue")
	axes[0].hlines(Vo, L+d/2.0, 1.5*L+d/2.0, linewidth=4.8, color="blue")
	axes[0].set_title('Probability Density for Even Wavefunctions', fontsize=25)

	# Defining the X ranges
	X_lef2 = np.linspace(-1.5*L-d/2.0, -L-d/2.0, 900,endpoint=True)
	X_lef1 = np.linspace(-L-d/2.0, -d/2.0, 900,endpoint=True)
	X_mid = np.linspace(-d/2.0, d/2.0, 900,endpoint=True)
	X_rig1 = np.linspace(d/2.0, L+d/2.0, 900,endpoint=True)
	X_rig2 = np.linspace(L+d/2.0, 1.5*L+d/2.0, 900,endpoint=True)

	# Plotting the probability densities
	for n in range(1,nstates+1):
	    k = np.sqrt(E_vals[n-1])*val
	    a0 = np.sqrt(Vo-E_vals[n-1])*val
	    a1 = np.sqrt(V1-E_vals[n-1])*val
	    str1="$n = "+str(n)+r"$, $E_{"+str(n)+r"} = %.3f$ eV"%(E_vals[n-1])
	    # Even solution wavefunctions
	    if (n%2==1):
	        B = amp/np.sqrt(f1(E_vals[n-1])*f1(E_vals[n-1])+1.0)
	        C = f1(E_vals[n-1])*B
	        A = (B*np.cos(k*d/2.0)+C*np.sin(k*d/2.0))/(np.exp(-a1*d/2.0)+np.exp(a1*d/2.0))
	        D = np.exp(a0*(L+d/2.0))*(B*np.cos(k*(L+d/2.0))+C*np.sin(k*(L+d/2.0)))
	        axes[0].plot(X_lef2, E_vals[n-1]+(D*np.exp(a0*X_lef2))**2, color="#ff4d4d", label="", linewidth=2.8)
	        axes[0].fill_between(X_lef2, E_vals[n-1], E_vals[n-1]+(D*np.exp(a0*X_lef2))**2, color="#3dbb2a")
	        axes[0].plot(X_lef1, E_vals[n-1]+(B*np.cos(k*X_lef1)-C*np.sin(k*X_lef1))**2, color="#ff4d4d", label="", linewidth=2.8)
	        axes[0].plot(X_mid,  E_vals[n-1]+(A*(np.exp(-a1*X_mid)+np.exp(a1*X_mid)))**2, color="#ff4d4d", label="", linewidth=2.8)
	        if(d>0.0): axes[0].fill_between(X_mid, E_vals[n-1], E_vals[n-1]+(A*(np.exp(-a1*X_mid)+np.exp(a1*X_mid)))**2, color="purple")
	        axes[0].plot(X_rig1, E_vals[n-1]+(B*np.cos(k*X_rig1)+C*np.sin(k*X_rig1))**2, color="#ff4d4d", label="", linewidth=2.8)
	        axes[0].plot(X_rig2, E_vals[n-1]+(D*np.exp(-a0*X_rig2))**2, color="#ff4d4d", label="", linewidth=2.8)
	        axes[0].fill_between(X_rig2, E_vals[n-1], E_vals[n-1]+(D*np.exp(-a0*X_rig2))**2, color="#3dbb2a")
	        axes[0].text(1.25*(L+d/2.0), E_vals[n-1]+0.01*Vo, str1, fontsize=16, color="#ff4d4d")

	# Drawing the backgroung graph
	axes[1].spines['right'].set_color('none')
	axes[1].xaxis.tick_bottom()
	axes[1].spines['left'].set_color('none')
	axes[1].axes.get_yaxis().set_visible(False)
	axes[1].spines['top'].set_color('none')
	axes[1].axis([-1.5*L-d/2.0,1.5*L+d/2.0,0.0,Ymax])
	axes[1].set_xlabel(r'$X$ (Angstroms)')
	str1="$V_o = %.3f$ eV"%(Vo)
	str11="$V_1= %.3f$ eV"% (V1)
	axes[1].text(1.05*(L+d/2.0), 1.02*Vo, str1, fontsize=24, color="blue")
	axes[1].text(-1.5*(L+d/2.0), 1.02*Vo, str1, fontsize=24, color="blue")
	if(d>0.0): axes[1].text(d/2, 1.02*Vo, str2, fontsize=24, color="blue")
	# Defining the maximum amplitude of the wavefunction
	if ((E_vals[1]-E_vals[0])/(E_vals[2]-E_vals[0]) < 0.2):
	    amp = np.sqrt((E_vals[2]-E_vals[0])/1.5)
	else:
	    amp = np.sqrt((E_vals[1]-E_vals[0])/1.5)
	# Plotting the energy levels
	for n in range(1,nstates+1):
	    # Odd solution
	    if (n%2==0): axes[1].hlines(E_vals[n-1], -1.5*L-d/2.0, 1.5*L+d/2.0, linewidth=1.8, linestyle='--', color="#800000")
	    # Even solution
	    if (n%2==1): axes[1].hlines(E_vals[n-1], -1.5*L-d/2.0, 1.5*L+d/2.0, linewidth=1.8, linestyle='--', color="#ff4d4d")
	    axes[1].margins(0.00)
	axes[1].vlines(-L-d/2.0, 0.0, Vo, linewidth=4.8, color="blue")
	if(d>0.0):
	    axes[1].vlines(-d/2.0, 0.0, V1, linewidth=4.8, color="blue")
	    axes[1].vlines(d/2.0, 0.0, V1, linewidth=4.8, color="blue")
	axes[1].vlines(L+d/2.0, 0.0, Vo, linewidth=4.8, color="blue")
	axes[1].hlines(Vo, -1.5*L-d/2.0, -L-d/2.0, linewidth=4.8, color="blue")
	axes[1].hlines(0.0, -L-d/2.0, -d/2.0, linewidth=4.8, color="blue")
	axes[1].hlines(V1, -d/2.0, d/2.0, linewidth=4.8, color="blue")
	axes[1].hlines(0.0, d/2.0, L+d/2.0, linewidth=4.8, color="blue")
	axes[1].hlines(Vo, L+d/2.0, 1.5*L+d/2.0, linewidth=4.8, color="blue")
	axes[1].set_title('Probability Density for Odd Wavefunctions', fontsize=25)

	# Defining the X ranges
	X_lef2 = np.linspace(-1.5*L-d/2.0, -L-d/2.0, 900,endpoint=True)
	X_lef1 = np.linspace(-L-d/2.0, -d/2.0, 900,endpoint=True)
	X_mid = np.linspace(-d/2.0, d/2.0, 900,endpoint=True)
	X_rig1 = np.linspace(d/2.0, L+d/2.0, 900,endpoint=True)
	X_rig2 = np.linspace(L+d/2.0, 1.5*L+d/2.0, 900,endpoint=True)

	# Plotting the wavefunctions
	for n in range(1,nstates+1):
	    k = np.sqrt(E_vals[n-1])*val
	    a0 = np.sqrt(Vo-E_vals[n-1])*val
	    a1 = np.sqrt(V1-E_vals[n-1])*val
	    str1="$n = "+str(n)+r"$, $E_{"+str(n)+r"} = %.3f$ eV"%(E_vals[n-1])
	    # Odd solution
	    if (n%2==0):
	        C = amp/np.sqrt(f3(E_vals[n-1])*f3(E_vals[n-1])+1.0)
	        B = f3(E_vals[n-1])*C
	        A = (B*np.cos(k*d/2.0)+C*np.sin(k*d/2.0))/(-np.exp(-a1*d/2.0)+np.exp(a1*d/2.0))
	        D = np.exp(a0*(L+d/2.0))*(B*np.cos(k*(L+d/2.0))+C*np.sin(k*(L+d/2.0)))
	        axes[1].plot(X_lef2, E_vals[n-1]+(D*np.exp(a0*X_lef2))**2, color="#800000", label="", linewidth=2.8)
	        axes[1].fill_between(X_lef2, E_vals[n-1], E_vals[n-1]+(D*np.exp(a0*X_lef2))**2, color="#3dbb2a")
	        axes[1].plot(X_lef1, E_vals[n-1]+(-B*np.cos(k*X_lef1)+C*np.sin(k*X_lef1))**2, color="#800000", label="", linewidth=2.8)
	        axes[1].plot(X_mid,  E_vals[n-1]+(A*(-np.exp(-a1*X_mid)+np.exp(a1*X_mid)))**2, color="#800000", label="", linewidth=2.8)
	        if(d>0.0): axes[1].fill_between(X_mid, E_vals[n-1], E_vals[n-1]+(A*(-np.exp(-a1*X_mid)+np.exp(a1*X_mid)))**2, color="purple")
	        axes[1].plot(X_rig1, E_vals[n-1]+(B*np.cos(k*X_rig1)+C*np.sin(k*X_rig1))**2, color="#800000", label="", linewidth=2.8)
	        axes[1].plot(X_rig2, E_vals[n-1]+(D*np.exp(-a0*X_rig2))**2, color="#800000", label="", linewidth=2.8)
	        axes[1].fill_between(X_rig2, E_vals[n-1], E_vals[n-1]+(D*np.exp(-a0*X_rig2))**2, color="#3dbb2a")
	        axes[1].text(1.25*(L+d/2.0), E_vals[n-1]+0.01*Vo, str1, fontsize=16, color="#800000")

	# Show the plots on the screen once the code reaches this point
	buf = io.BytesIO()
	plt.savefig(buf, format='png')
	buf.seek(0)  # rewind the data
	sys.stdout.flush()
	sys.stdout.buffer.write(buf.getvalue())
