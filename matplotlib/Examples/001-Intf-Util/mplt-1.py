import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.ticker import ScalarFormatter

xfmt = ScalarFormatter()
xfmt.set_powerlimits((-3,3))
x_time = []
out_value = []
in_value = []

with open('results.txt', 'r') as f:
    for line in f.readlines():
        line = eval(line)
        x_time.append(dates.datestr2num(line['Time']))
        out_value.append(int(line['Gig0-0_Out_uPackets']))
        in_value.append(int(line['Gig0-0_In_uPackets']))
    plt.subplots_adjust(bottom=0.3, left=0.2)
    plt.xticks(rotation=45)
    plt.plot_date(x_time, out_value, 'b-')
    plt.plot_date(x_time, in_value, 'g-')
    plt.gca().xaxis.set_major_formatter(dates.DateFormatter("%d-%m\
#%H:%M:%S"))
    plt.gca().yaxis.set_major_formatter(xfmt)
    plt.ticklabel_format(axis='y',style='sci',scilimits=(1,4))
    ## yscale values: 'linear', 'log', 'symlog', 'asinh', 'logit', 'function', 'functionlog'
    plt.yscale('symlog')
    plt.title('Router1 G0/0')
    plt.xlabel('Time in UTC')
    plt.ylabel('Unicast Packets')
    plt.savefig('result.png')
    plt.legend(['Output Unicast Packets', 'Input Unicast Packets'])
    plt.show()
