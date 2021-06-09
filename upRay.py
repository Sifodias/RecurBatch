import os
import argparse
import pathlib
import multiprocessing as mp

jobs = mp.JoinableQueue()

def workerRoutine(jobs):
    while True:
        job = jobs.get()
        os.system(job)
        jobs.task_done()


def preprocess_path(path, cmd=False):
    if path[-1] != '/' and cmd is False:
        path += '/'
    if path[0] == '.':
        path = path[1:]
        if path[0] != '/':
            path = os.getcwd() + '/' + path
        else:
            path = os.getcwd() + path
    path = path.replace('\ ', ' ')
    return path


def recDir(cmd, input):
    for obj in os.scandir(input):
        if obj.is_file():
            exec = cmd
            exec = exec.replace('#1', '\"' + obj.path + '\"')
            exec = exec.replace('#2', '\"' + os.getcwd() + '/' + obj.name + '\"')
            jobs.put(exec)
            
        else:
            os.makedirs("./" + obj.name, exist_ok=True)
            os.chdir("./" + obj.name)
            recDir(cmd, input + obj.name + "/")
            os.chdir("..")

def main():
    parser = argparse.ArgumentParser(description='Batch process files recursively')
    parser.add_argument('-i', '--input', help="The input directory")
    parser.add_argument('-o', '--output', help="The output directory")
    parser.add_argument('-t', '--threads', help="Number of threads to process the files", type=int, default=1)
    parser.add_argument('cmd',  help='The command you want to execute on each file. \
                                        \nThe command should have the format \"prog [...] #1 [...] #2 [...]\" \
                                        Where #1 will be replaced by the path of the currently processed file,\n \
                                        and #2 will be replaced by its output path')
    # type=pathlib.Path,
    args = parser.parse_args()

    if args.input is None or args.output is None or args.cmd is None:
        print("Please provide input and output paths, and a command to execute")
        return

    args.cmd = preprocess_path(args.cmd, cmd=True)
    args.input = preprocess_path(args.input)
    args.output = preprocess_path(args.output)
    
    pool = list()
    for _ in range(args.threads):
        worker = mp.Process(target=workerRoutine, args=(jobs,))
        worker.start()
        pool.append(worker)

    try:
        os.makedirs(args.output, exist_ok=True)
        os.chdir(args.output)
        recDir(args.cmd, args.input)
        jobs.join()

    except KeyboardInterrupt:
        jobs.close()
    
    for w in pool:
        w.terminate()

        
if __name__=="__main__":
    main()
