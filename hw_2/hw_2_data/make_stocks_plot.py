import numpy as np
from matplotlib import pyplot as plt


# Read in data from tab-delimited files
nydata = np.genfromtxt("ny_temps.txt", delimiter="\t")
googledata = np.genfromtxt("google_data.txt", delimiter="\t")
yahoodata = np.genfromtxt("yahoo_data.txt", delimiter="\t")


# Slice rows from 1 since I don't need the column titles
ny_dates = nydata[1:,0]
ny_temps = nydata[1:,1]

goog_dates = googledata[1:,0]
goog_stocks = googledata[1:,1]

yahoo_dates = yahoodata[1:,0]
yahoo_stocks = yahoodata[1:,1]


# Create the plot
# ax1 first
fig, ax1 = plt.subplots()

plt.title("New York Temperature, Google, and Yahoo!",
          fontsize=14, fontweight="bold")

ln1 = ax1.plot(goog_dates, goog_stocks, color="blue", 
               label="Google Stock Value")
ln2 = ax1.plot(yahoo_dates, yahoo_stocks, color="purple", 
               label="Yahoo! Stock Value")

ax1.set_xlabel("Date (MJD)", fontsize=8)
ax1.set_ylabel("Values (Dollars)", fontsize=8)

ax1.minorticks_on()
ax1.tick_params(which="both", direction="in", labelsize=6)
ax1.tick_params(which="major", length=6, width=1.5)
ax1.tick_params(top=False)

# then ax2
ax2 = ax1.twinx()

ln3 = ax2.plot(ny_dates, ny_temps, "r--",
               label="NY Mon. High Temp")

ax2.set_ylabel("Temperature (\u2109)", fontsize=8)

ax2.set_ylim(-150,100)
ax2.set_xlim(48800, 55600)

ax2.minorticks_on()
ax2.tick_params(which="both", direction="in", labelsize=6)
ax2.tick_params(which="major", length=6, width=1.5) 
               
# setup the combined legend
lns = ln2 + ln1 + ln3
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=(0.05, .47), frameon=False,
           fontsize="x-small")

# and change the linewidth of the frame
for axis in ["top","bottom","left","right"]:
      ax2.spines[axis].set_linewidth(1.5)


plt.savefig("my_stocks.png")
plt.show()












