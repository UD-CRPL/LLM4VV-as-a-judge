#!/bin/bash -l

scratch_dir="./scratch/"
output_dir="./outputs/"
log_dir="./logs/"

#Check for merge functionality
if [[ $* == *--merge* ]]
then

python << EoF
import json, glob
output_directory = "${output_dir}"
data = []
for filename in glob.glob(output_directory+"*"):
    with open(filename, 'r', encoding='utf-8') as f: data += json.load(f)
with open(output_directory+"final_results.json", 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
EoF

exit
fi

#Main Script Start
if [ "$#" -ne 3 ]; then
  echo 'Arguments must be in the form <batch file> <input file> <number of processes>'
  exit
fi

batch_file=$1
data_file=$2
num_nodes=$3
script_content=$(<$batch_file)

rm -rf $scratch_dir
rm -rf $log_dir

mkdir -p $scratch_dir
mkdir -p $output_dir
mkdir -p $log_dir

module load python
conda activate myenv

#Shard data

python << EoF
import json

data_file, num_nodes, scratch_dir = "${data_file}", "${num_nodes}", "${scratch_dir}"

with open(data_file, 'r', encoding='utf-8') as f: data = json.load(f)

total_num = len(data)
chunk_size = (total_num // int(num_nodes)) + 1
separated_data = [data[i:i+chunk_size] for i in range(0, total_num, chunk_size)]

count = 0
for subset in separated_data:
    with open(scratch_dir+f"subset_{count}.json", 'w', encoding='utf-8') as f: json.dump(subset, f)
    count += 1

EoF



#Launch tasks

sed "1a\
#SBATCH --array=0-$((num_nodes - 1))\n#SBATCH --output=${log_dir}subset_%a_log.out" $batch_file > "${scratch_dir}batch.sh"

start_line_raw=$(grep -n "#BEGIN" "${scratch_dir}batch.sh")
start_line=${start_line_raw%:*}
sed "${start_line}a\
output_file=\"./outputs/subset_\${SLURM_ARRAY_TASK_ID}.json\"; data_file=\"./scratch/subset_\${SLURM_ARRAY_TASK_ID}.json\" " "${scratch_dir}batch.sh" > "${scratch_dir}batch2.sh"

sbatch "${scratch_dir}batch2.sh"

#echo -e "#!/bin/bash\noutput_file=\$1\ndata_file=\$2\nlog_file=\$3\ncat <<EoF\n${script_content}\nEoF"  > "${scratch_dir}parent_script.sh"
#chmod +x "${scratch_dir}parent_script.sh"
#for (( i=0; i<num_nodes; i++ ))
#do
#  ( ./"${scratch_dir}parent_script.sh" "${output_dir}subset_${i}.json" "${scratch_dir}subset_${i}.json" "${log_dir}subset_${i}_log.txt"  > "${scratch_dir}task_${i}_${batch_file}"; \
#  chmod +x "${scratch_dir}task_${i}_${batch_file}"; \
#  sbatch "${scratch_dir}task_${i}_${batch_file}" ) &
#done
#echo "Launching jobs..."
#sleep 10
#echo -e "Jobs Launched!\n"

#Wait for tasks to finish

while [ $(squeue -u "$USER" -h -t pending,running -r | wc -l) -ne 0 ]
do
  echo -e "\e[KWaiting for jobs to complete (Pending: $(squeue -u $USER -h -t pending -r | wc -l ) | Running: $(squeue -u $USER -h -t running -r | wc -l ))..."
  sleep 5
done


#Concatenate Outputs
python << EoF
import json, glob
output_directory = "${output_dir}"
data = []
for filename in glob.glob(output_directory+"*"):
    with open(filename, 'r', encoding='utf-8') as f: data += json.load(f)
with open(output_directory+"final_results.json", 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
EoF

echo "Concatenated outputs!"
