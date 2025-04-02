import os
import sys
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def run_test(outfile='test.out', maxcores=20, test='ramp_fit',
    ramp_method='OLS_C'):

    benchmark_data=[]
    for cores in np.arange(maxcores):

        cores=cores+1
        print(f'ncores = {cores}')

        cmd = f'python jwst_benchmark.py {cores} {test} {ramp_method} > {outfile} 2>&1'
        print(cmd)
        os.system(cmd)

        times = []
        with open(outfile, 'r') as f:
            for line in f:
                if test=='ramp_fit' and 'Ramp Fitting C Time' in line:
                    times.append(str(line.split(':')[-1].strip()))
                if test=='jump' and 'jump' in line and 'execution time in seconds' in line:
                    times.append(str(line.split(':')[-1].strip()))

        if len(times)==0:
            raise Exception(f'Benchmark for {cores} cores did not run successfully')

        if os.path.exists(outfile):
            os.remove(outfile)

        benchmark_data.append((cores, times))

    return(benchmark_data)

def save_benchmark(benchmark_data, outfile='benchmark.csv'):

    with open(outfile,'w') as f:
        f.write('cores,times\n')
        for row in benchmark_data:
            times = ' '.join(row[1])
            f.write(f'{row[0]},{times}\n')

def load_benchmark(infile='benchmark.csv'):

    benchmark_data=[]
    with open(infile,'r') as f:
        for line in f:
            if 'cores' in line: continue
            cores,times=line.split(',')
            times = times.split()
            cores = float(cores)
            times = [float(t) for t in times]
            benchmark_data.append((cores, times))

    return(benchmark_data)

def plot_benchmark(benchmark_data, pltfile='benchmark.png'):

    norm=1.0
    if float(benchmark_data[0][0])==1.0:
        norm = benchmark_data[0][1][0]

    fig, ax = plt.subplots()

    avgdata = []
    mindata = []
    for i in np.arange(len(benchmark_data)):
        cores=benchmark_data[i][0]
        avg=np.median([float(v) for v in benchmark_data[i][1]])
        mnn=np.max([float(v) for v in benchmark_data[i][1]])
        avgdata.append((cores, avg))
        mindata.append((cores, mnn))
        for val in benchmark_data[i][1]:
            ax.plot([float(cores)], [norm/float(val)], marker='o', color='red')
        #ax.plot([float(cores)], [norm/avg], marker='*', color='blue', ms=10)

    def func(x, a):
        return(x*a)

    maxcores = np.max([c[0] for c in benchmark_data])
    ax.plot(np.arange(maxcores)+1.0, np.arange(maxcores)+1.0,
        linestyle='dashed', color='k')

    # Calculate average improvement
    popt, pcov = curve_fit(func, [d[0] for d in avgdata], [norm/d[1] for d in avgdata])
    avgfactor = float('%.4f'%popt[0])

    # Calculate rate-limiting improvement
    z = np.polyfit([d[0] for d in mindata], [norm/d[1] for d in mindata], 1)
    p = np.poly1d(z)
    minfactor = float('%.4f'%z[0])
    constant = float('%.4f'%z[1])
    ax.plot(np.arange(maxcores)+1.0, p(np.arange(maxcores)+1.0),
        linestyle='dashed', color='green')

    ylim = np.max([10, np.max([norm/d[1] for d in avgdata])])
    ax.text(float(maxcores)/2, 0.54*ylim, 'Linear', rotation=33.0)
    ax.text(maxcores, 0.75, f'Rate-limiting time = Ncores * {minfactor} + {constant}', color='green', ha='right')

    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Run time improvement (scaled to 1 core)')

    if 'ramp_fit' in pltfile:
        ax.set_title('stcal.ramp_fitting')
    elif 'jump' in pltfile:
        ax.set_title('stcal.jump')

    plt.savefig(pltfile)


if __name__=="__main__":

    test='ramp_fit'
    maxcores = 10
    redo = True

    ramp_method='OLS_C'

    if test=='ramp_fit':
        m=f'_method{ramp_method}'
    else:
        m=''

    benchmark_file=f'{test}{m}_benchmark_{maxcores}cores.csv'
    outfile=f'{test}{m}_test.out'
    pltfile=f'{test}{m}_benchmark_{maxcores}cores.png'

    if redo:
        benchmark_data=run_test(outfile=outfile, maxcores=maxcores, test=test,
            ramp_method=ramp_method)
        save_benchmark(benchmark_data, outfile=benchmark_file)

    benchmark_data=load_benchmark(infile=benchmark_file)
    plot_benchmark(benchmark_data, pltfile=pltfile)

