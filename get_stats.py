import sys, json

datafile = sys.argv[1]

with open(datafile, 'r') as f: data = json.load(f)


total_files = len(data)
id_counts = [0]*6

pipeline_mistakes_1 = [0]*6
pipeline_mistakes_2 = [0]*6
llmj_mistakes_1 = [0]*6
llmj_mistakes_2 = [0]*6
nocomp_mistakes_1 = [0]*6
nocomp_mistakes_2 = [0]*6

for file in data:
    valid = 0 if file['correct']=='y' else 1
    i = file['issue_id']
    id_counts[i] += 1

    pipeline_mistakes_1[i] += 0 if file['file_correct_1'] == valid else 1
    pipeline_mistakes_2[i] += 0 if file['file_correct_2'] == valid else 1

    llmj_mistakes_1[i] += 0 if file['llmj_correct_1'] == valid else 1
    llmj_mistakes_2[i] += 0 if file['llmj_correct_2'] == valid else 1

    nocomp_mistakes_1[i] += 0 if ((valid==0) and file['llmj_correct_1']==valid) or (file['file_correct_1']==valid) else 1
    nocomp_mistakes_2[i] += 0 if ((valid==0) and file['llmj_correct_2']==valid) or (file['file_correct_2']==valid) else 1

print(f"\nIssue distribution: {id_counts}")
print(f"Total files: {total_files}")

print(f"\nPipeline 1 profile: {pipeline_mistakes_1}\nPipeline 2 profile: {pipeline_mistakes_2}")
print(f"\nPipeline 1 w/o comp errors profile: {nocomp_mistakes_1}\nPipeline 2 w/o comp errors profile: {nocomp_mistakes_2}")
print(f"\nLLMJ 1 profile: {llmj_mistakes_1}\nLLMJ 2 profile: {llmj_mistakes_2}\n")

print(f"\nPipeline 1 accuracy: {1 - sum(pipeline_mistakes_1)/total_files}\nPipeline 2 accuracy: {1 - sum(pipeline_mistakes_2)/total_files}")
print(f"\nPipeline 1 w/o comp errors accuracy: {1 - sum(nocomp_mistakes_1)/total_files}\nPipeline 2 w/o comp errors accuracy: {1 - sum(nocomp_mistakes_2)/total_files}")
print(f"\nLLMJ 1 accuracy: {1 - sum(llmj_mistakes_1)/total_files}\nLLMJ 2 accuracy: {1 - sum(llmj_mistakes_2)/total_files}\n")
