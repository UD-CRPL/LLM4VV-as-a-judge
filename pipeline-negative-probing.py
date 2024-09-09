import json, sys, os, shutil, LLMJ, validation_pipeline, torch, time
from transformers import AutoTokenizer, AutoModelForCausalLM

start_time = time.time()


filesuite_dir = "./omp-filesuite"
acc_headers_dir = "./acc_headers"
omp_headers_dir = "./omp_headers" 
mode = "OpenMP"

input_data_file = sys.argv[1]
output_data_file = sys.argv[2]

#try:
#    shutil.rmtree(filesuite_dir)
#except:
#    pass
try:
    os.mkdir(filesuite_dir)
except:
    pass

if mode == "OpenMP":
    header_files = [f for f in os.listdir(omp_headers_dir) if f.endswith('.h')]
    for header_file in header_files:
        shutil.copy(os.path.join(omp_headers_dir, header_file), filesuite_dir)
elif mode == "OpenACC":
    header_files = [f for f in os.listdir(acc_headers_dir) if f.endswith('.h')]
    for header_file in header_files:
        shutil.copy(os.path.join(acc_headers_dir, header_file), filesuite_dir)


with open(input_data_file, 'r') as f: data = json.load(f)

#Labeled Suite Preprocessing

print("Preprocessing files...")
new_data = []
for file in data:
    base_filename = (file['filename'].split('/')[-1].split('\\')[-1]).split('.')
    good_filename = base_filename[0]+f'_(GOOD).{base_filename[-1]}'
    bad_filename = base_filename[0]+f'_(BAD).{base_filename[-1]}'
    new_data.append({
        "filename": good_filename,
        "correct": 'y',
        "issue": "None",
        "issue_id": 5,
        "code": file['original_code']
    })
    new_data.append({
        "filename": bad_filename,
        "correct": 'n',
        "issue": file['issue'],
        "issue_id": file['issue_id'],
        "code": file['error_code']
    })

data = new_data

files = []

print("Creating physical files...")

for file in data:
    filepath = filesuite_dir + '/' + file['filename']
    with open(filepath, 'w') as f: f.write(file['code'])
    file['filename'] = filepath
    files.append(file)

print("Done!")



print(f"Available memory on GPU 0: {torch.cuda.get_device_properties(0).total_memory}")
model_id = "deepseek-ai/deepseek-coder-33b-instruct"
print("Initializing tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
print("Initializing model...")
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2", device_map="auto")
print("Done!")

total, correct_1, correct_2, llmj_correct_judge_1, llmj_correct_judge_2 = 0, 0, 0, 0, 0

outputs = []

for file in files:
    print(f"Processing file {file['filename']}...")
    filedata = validation_pipeline.Validate(file['filename'], model, tokenizer, mode)
    file.update(filedata)
    #outputs.append(file)
    file_correct_1 = 0 if (filedata['comp_return_code']==0) and (filedata['run_return_code']==0) and (filedata['llmj_eval']==0) else 1
    #file_llmj_correct = 0 if filedata['llmj_eval']==0 else 1
    file_correct_2 = 0 if (filedata['comp_return_code']==0) and (filedata['run_return_code']==0) and (filedata['llmj_alt_eval']==0) else 1
    llmj_correct_1 = 0 if filedata['llmj_eval']==0 else 1
    llmj_correct_2 = 0 if filedata['llmj_alt_eval']==0 else 1

    #TODO:
    #Calculate Pipeline output with both llmj_eval and llmj_alt_eval
    #Adjust above variables so correct_1 is number of correct judgements with llmj_eval,
    #correct_2 is number of correct judgements with llmj_alt_eval,
    # and llmj_correct_1 and llmj_correct_2 are number of correct judgements from LLMJ alone using eval and alt_eval respectively
    #Append these values to the output dict for each file
    file.update({
        "file_correct_1": file_correct_1,
        "file_correct_2": file_correct_2,
        "llmj_correct_1": llmj_correct_1,
        "llmj_correct_2": llmj_correct_2
    })
    outputs.append(file)
    total += 1
    correct_1 += 1 if file_correct_1==0 else 0
    correct_2 += 1 if file_correct_2==0 else 0
    llmj_correct_judge_1 += 1 if llmj_correct_1==0 else 0
    llmj_correct_judge_2 += 1 if llmj_correct_2==0 else 0
    print(f"Current accuracies: {correct_1/total} | {correct_2/total}\nCurrent LLMJ accuracies: {llmj_correct_judge_1/total} | {llmj_correct_judge_2/total}\n\n")

#TODO: Dump outputs to json file specified above

with open(output_data_file, "w") as f: json.dump(outputs, f, indent=4)

end_time = time.time()

print(f"\n\nSTART TIME: {start_time}\nEND TIME: {end_time}\nTOTAL RUNTIME: {end_time-start_time}")
