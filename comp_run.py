
import os, sys, subprocess, time, json, glob


def Validation(file_path, model, tokenizer, pp_model):
    comp = compliation(file_path, pp_model)
    run = execution(file_path, pp_model, comp)
    return comp.update(run)




def compliation(file_path, pp_model):
    
    language = file_path[file_path.rfind(".")+1:].lower()
    flavor = 0 if pp_model == "OpenMP" else 1
    
    compilers = [{
        "c": ["clang", "-lm", "-fopenmp", "--offload-arch=native", "-I.", "-O3", "-o", "omp.out", file_path],
        "cpp": ["clang++", "-lm", "-fopenmp", "--offload-arch=native", "-I.", "-O3", "-o", "omp.out", file_path],
        #"c": ["gcc", '-foffload=-lm -latomic', "-lm", "-fopenmp", "-o", "omp.out", file_path],
        #"cpp": ["g++", '-foffload=-lm -latomic', "-lm", "-fopenmp", "-o", "omp.out", file_path],
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

if __name__=="__main__":
    total, correct = 0, 0
    data = []
    file_dir = "./omp-filesuite/*"
    for file in glob.glob(file_dir):
        print(f"Processing file {file}...      ")
        comp = compliation(file, 'OpenMP')
        run = execution(file, 'OpenMP', comp)
        comp.update(run)
        data += comp
        total += 1
        if comp['comp_return_code'] == 0: correct += 1
        if "(GOOD)" in file and comp['comp_return_code'] != 0: print(f"\n\n{file}:  {comp['comp_return_code']}\n\n{comp['comp_stderr']}\n\n\n")
        #print(f"( {comp['comp_return_code']} | {comp['run_return_code']} )")
    with open("comp-run-data.json", 'w') as f: json.dump(data, f, indent=4)
    print(f"\n\nFinal valid percentage: {correct/total}\n")
