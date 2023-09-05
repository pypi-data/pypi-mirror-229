import subprocess

def predict_geneid(geneid_executable, parameter_file, sequence):
    command = [geneid_executable, "-P", parameter_file, sequence]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Error running geneid: {e.stderr}")

#Change command according to the requirements
# General
# command = [geneid_executable, "-P", parameter_file, sequence]
# Prediction of acceptor splice sites
# command = [geneid_executable, "-P", parameter_file, -ao, sequence]
# Prediction of exons
# command = [geneid_executable, "-P", parameter_file, -xo, sequence]
# Gene prediction
# command = [geneid_executable, "-vP", parameter_file, -xo, sequence]
# Improving gene prediction by using re-annotation
# command = [geneid_executable, "-G", sequence]
# more information can be found at the website https://genome.crg.es/software/geneid/.