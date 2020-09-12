import random
import matplotlib.pyplot as plt
from matplotlib.animation  import *
from itertools import count

x=[] #counter or timer
y=[] #data

index=count()

def animation(i):
	x.append(next(index))
	y.append(random.randint(0,255))
	plt.plot(x,y)
	plt.plot()
	#cla is to clear out the axis so that the plots dont get stacked on top of each other

animate=FuncAnimation(plt.gcf(),animation,interval=1000)
#interval=1000 means 1sec
#gcf is get current figure

plt.tight_layout()
plt.show()