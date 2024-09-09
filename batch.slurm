#!/bin/bash -l
#SBATCH --account=m4093
#SBATCH --time=4:00:00
#SBATCH --constraint=gpu
#SBATCH --gpus=4
#SBATCH --qos=regular
#SBATCH --mem=200G
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1

#BEGIN

module load python
module load nvidia
module use /global/cfs/cdirs/m4093/modulefiles/
module load llvm/19.0.0

conda activate myenv

export HF_HOME="/pscratch/sd/z/zacksoll/.cache"
export HUGGINGFACE_HUB_CACHE="/pscratch/sd/z/zacksoll/.cache"

srun python pipeline-negative-probing.py $data_file $output_file
