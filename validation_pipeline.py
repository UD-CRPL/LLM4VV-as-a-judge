
import os, sys, subprocess, time, json, LLMJ


def Validate(file_path, model, tokenizer, pp_model):
    comp = compilation(file_path, pp_model)
    run = execution(file_path, pp_model, comp)
    final = LLMJ.judge_file(file_path, model, tokenizer, pp_model, comp, run)
    return final




def compilation(file_path, pp_model):
    
    language = file_path[file_path.rfind(".")+1:].lower()
    flavor = 0 if pp_model == "OpenMP" else 1
    
    compilers = [{
        "c": ["clang", "-lm", "-fopenmp", "--offload-arch=native", "-I.", "-O3", "-o", "omp.out", file_path],
        "cpp": ["clang++", "-lm", "-fopenmp", "--offload-arch=native", "-I.", "-O3", "-o", "omp.out", file_path],
        "f90": ["gfortran", "-foffload=-lm -latomic", "-lm", "-fopenmp", "-o", "omp.out", file_path]
    },{
        "c": ["nvc", "-acc", "-Minfo=all", "-o", "acc.out", file_path],
        "cpp": ["nvc++", "-acc", "-Minfo=all", "-o", "acc.out", file_path],
        "f90": ["nvfortran", "-acc", "-Minfo=all", "-o", "acc.out", file_path]
    }]

    comp_stdout = ""
    comp_stderr = ""
    try:
        compile_data = subprocess.run(compilers[flavor][language], capture_output=True, text=True, timeout=30)
        comp_return_code = compile_data.returncode
        comp_stdout = compile_data.stdout
        comp_stderr = compile_data.stderr
    except Exception as e:
        print(f"Encountered problem compiling file, skipping...\nError: {e}")
        comp_return_code = -2
        comp_stdout = ""
        comp_stderr = f"Python: Encountered error during compilation:\n\n{e}"
    return {
            "comp_return_code": comp_return_code,
            "comp_stdout": comp_stdout,
            "comp_stderr": comp_stderr
            }

def execution(file_path, pp_model, comp):
    exe = "./omp.out" if pp_model == "OpenMP" else "./acc.out"
    if comp["comp_return_code"] == 0:
        try:
            run_data = subprocess.run([exe], capture_output=True, text=True, timeout=30)
            return_code = run_data.returncode
            stdout = run_data.stdout
            stderr = run_data.stderr
        except Exception as e:
            return_code=-1
            stdout=""
            stderr=f"Python: Problem encountered when running file:\n\n{e}"
    else:
        return_code = -1
        stdout = ""
        stderr="Python: File did not compile!"
    
    return {
            "run_return_code": return_code,
            "run_stdout": stdout,
            "run_stderr": stderr
            }

#Validation("/Users/jay/CRPL/LLMValidationPipeline/test.c","model","token","OpenACC")
