import sys, glob, statistics

file_dir = sys.argv[1]

times = []
totals = []
for file in glob.glob(f"{file_dir}/*"):
    with open(file, 'r') as f: content = f.read()
    try:
        start = content.split("START TIME: ")[1].split('\n')[0]
        end = content.split("END TIME: ")[1].split('\n')[0]
        times.append(float(start))
        times.append(float(end))
        totals.append(float(end)-float(start))
    except:
        pass

times = sorted(times, key=float)

average_runtime = sum(totals) / len(totals)
median = statistics.median(totals)

runtime = times[-1] - times[0]
print(f"Earliest start time: {times[0]}\nLatest end time: {times[-1]}")
print(f"Total time in seconds: {runtime}\nTotal time: {int(runtime//3600)}:{int((runtime%3600)//60)}:{int((runtime%60)//1)}")
print(f"Average time in seconds for {len(totals)} processes: {average_runtime}\nAverage time: {int(average_runtime//3600)}:{int((average_runtime%3600)//60)}:{int((average_runtime%60)//1)}")
print(f"Median time: {int(median//3600)}:{int((median%3600)//60)}:{int((median%60)//1)}")
