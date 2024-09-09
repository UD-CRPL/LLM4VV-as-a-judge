from transformers import AutoTokenizer, AutoModelForCausalLM
from termcolor import colored
import os, sys, json, time, torch



def initialize_model():
    print(f"Available memory on GPU 0: {torch.cuda.get_device_properties(0).total_memory}")
    model_id = "deepseek-ai/deepseek-coder-33b-instruct"
    print("Initializing tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    print("Initializing model...")
    model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2", device_map="auto")
    print("Done!")
    return model, tokenizer

def generate_response(prompt, model, tokenizer):
    messages = [{'role':'user', 'content':prompt}]

    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
    outputs = model.generate(inputs, max_new_tokens=2048, do_sample=False, top_k=50, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
    return response.strip()



def judge_file(file_path, model, tokenizer, mode, comp_data, run_data):

    comp_data.update(run_data)
    file_data = comp_data

    with open(file_path, 'r') as f: file_content = f.read()

    flavor = "OpenACC" if mode=='acc' or mode=='OpenACC' else 'OpenMP'

    prompt1 = f"""
Review the following {flavor} compiler test and evaluate it based on the following criteria:
1. Usage: Verify that the file invokes or utilizes {flavor} directives and routines.
2. Syntax: Ensure all {flavor} directives and routines are syntactically correct.
3. Directive Appropriateness: Check if the right directives are used for the intended parallel computations.
4. Clause Correctness: Verify that all clauses within the directives are correctly used according to {flavor} specifications.
5. Memory Management: Asses the accuracy of data movement between the CPU and the GPU.
6. Compliance: Ensure the code adheres to the latest {flavor} specifications and best practices.
7. Logic: Verify that the logic of the compiler test is correct.

Based on these criteria, evaluate the code and determine if it is a valid or invalid test. Think step by step.
You MUST include the exact phrase, "FINAL JUDGEMENT: valid" in your response if you deem the test to be valid.
If you deem the test to be invalid, include the exact phrase "FINAL JUDGEMENT: invalid" in your response instead.

Here is some information about the code to help you.

When compiled with a compliant {flavor} compiler, the below code causes the following outputs:
Compiler return code: {file_data['comp_return_code']}
Compiler STDERR: {file_data['comp_stderr']}
Compiler STDOUT: {file_data['comp_stdout']}

When the compiled code is run, it gives the following results:
Return code: {file_data['run_return_code']}
STDOUT: {file_data['run_stdout']}
STDERR: {file_data['run_stderr']}

Here is the code:
{file_content}
"""
    prompt2 = f"""
Describe what the below {flavor} program will do when run. Think step by step.
Here is some information about the code to help you; you do not have to compile or run the code yourself.

When the below code is compiled with a {flavor}-compliant compiler, the compiler gives the following outputs:
Compiler return code: {file_data['comp_return_code']}
Compiler STDERR: {file_data['comp_stderr']}
Compiler STDOUT: {file_data['comp_stdout']}

When the compiled code is run, it gives the following results:
Return code: {file_data['run_return_code']}
STDOUT: {file_data['run_stdout']}
STDERR: {file_data['run_stderr']}

Using this information, describe in great detail how the below code works, what the below code will do when run, and suggest why the
below code might have been written this way. Then, based on that description, determine whether the described program would
be a valid or invalid compiler test for {flavor} compilers. You MUST include the exact phrase "FINAL JUDGEMENT: valid" in
your final response if you beleive that your description of the below {flavor} code describes a valid compiler test;
otherwise, your final response MUST include the exact phrase "FINAL JUDGEMENT: invalid".

Here is the code for you to analyze:
{file_content}
"""
    response = generate_response(prompt1, model, tokenizer)
    alt_response = generate_response(prompt2, model, tokenizer)

    print(colored("\n\n\n\n\n\n***** First Prompt Result *****\n\n", 'yellow'))
    print(colored(prompt1 + '\n\n' + response, 'green'))
    print(colored("\n\n\n***** Second Prompt Results *****\n\n", 'yellow'))
    print(colored(prompt2 + '\n\n' + alt_response, 'green'))


    llm_eval = 0 if "final judgement: valid" in response.lower() or "final judgement: the code is valid" in response.lower() else 1
    llm_alt_eval = 0 if "final judgement: valid" in alt_response.lower() or "final judgement: the code is valid" in alt_response.lower() else 1
    file_data.update({
        "llmj_eval": llm_eval,
        "llmj_review": response,
        "llmj_alt_eval": llm_alt_eval,
        "llmj_alt_review": alt_response})
    return file_data















