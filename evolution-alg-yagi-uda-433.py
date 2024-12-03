import necpp
import os
import json
import random
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt



WireGene = Enum('WireGene', [('EXISTANCE', 0), ('DISTANCE', 1), ('LENGTH', 2)])



def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())



def calc_yagi(chromosome, params, calc_result="gain"):

    segments = 21
    height = 10.2
    wire_thickness = 2.55e-4

    if not chromosome[0][0]:
        return 0.0

    # Respect minimal distance
    for id in range(len(chromosome)-1):
        for id2 in range(id+1, len(chromosome)):
            # soft exception if they are both active
            if chromosome[id][0] and chromosome[id2][0] and (abs(chromosome[id][1] - chromosome[id2][1]) < params["distance_step"]):
                return 0.0


    # Calculate antenna radiation
    nec = necpp.nec_create()
    handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[0][2]/2, height, 0, chromosome[0][2]/2, height, 0, wire_thickness, 1, 1))

    if (len(chromosome) > 0) and chromosome[1][0]:
        handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[1][2]/2, height, -chromosome[1][1], chromosome[1][2]/2, height, -chromosome[1][1], wire_thickness, 1, 1))
    if (len(chromosome) > 1):
        for director in chromosome[2:]:
            if director[0]:
                handle_nec(necpp.nec_wire(nec, 1, segments, -director[2]/2, height, director[1], director[2]/2, height, director[1], wire_thickness, 1, 1))

    handle_nec(necpp.nec_geometry_complete(nec, 0))
    handle_nec(necpp.nec_fr_card(nec, 0, 1, params["freq"], 0))
    handle_nec(necpp.nec_ex_card(nec, 0, 1, 11, 1, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)) 
    handle_nec(necpp.nec_rp_card(nec, 0, 360, 1000, 0, 0, 0, 0, 90.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 1, 1000, 0, 0, 0, 0, -90.0, 0.0, 0.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 91, 120, 0, 0, 0, 0, 0.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    result_index = 0
    
    match calc_result:
        case "impedance":
            result = complex(necpp.nec_impedance_real(nec,result_index), 
                        necpp.nec_impedance_imag(nec,result_index))
        case "gain":
            result = necpp.nec_gain_max(nec, 0)
        case _:
            raise(f"calc_result expected to be in 'gain', 'impedance', but is: {calc_result}")
    
    necpp.nec_delete(nec)

    return result



def random_gene(gene_cluster_id, gene_type: [WireGene], params):
    existance = lambda a: (False if a<0.5 else True)
    match gene_type:
        case WireGene.EXISTANCE:
            return True if (gene_cluster_id == 0) else existance(random.uniform(0, 1))
        case WireGene.DISTANCE:
            return  0.0 if (gene_cluster_id == 0) else params["distance_step"]*random.randint(0, params["max_distance_steps"])
        case WireGene.LENGTH:
            return random.uniform(params["wire_len_limits"][0], params["wire_len_limits"][1])



def random_chromosome(params):
    if not isinstance(params["num_elements"], int):
        raise("num_elements must be a positive integer")
    if params["num_elements"] < 1:
        raise("Chromosome must have at least one wire (dipole), but has none.")
    return [(random_gene(id, WireGene.EXISTANCE, params), random_gene(id, WireGene.DISTANCE, params), random_gene(id, WireGene.LENGTH, params)) for id in range(params["num_elements"])]



def initialize_population(params):
    return [random_chromosome(params) for _ in range(params["population_size"])]



def calculate_fitness(population, params):
    if os.path.exists(params["fitness_scores_file"]):
        with open(params["fitness_scores_file"], 'r') as f:
            scores_list = json.load(f)
    else:
        scores_list = {}

    population_with_fitness = []
    for chromosome in population:
        if not str(chromosome) in scores_list.keys():
            try:
                score = calc_yagi(chromosome, params)
            except:
                score = 0.0
            finally:
                scores_list[str(chromosome)] = score


        population_with_fitness.append((chromosome, scores_list[str(chromosome)]))

    with open(params["fitness_scores_file"], 'w') as f:
        json.dump(scores_list, f)
    
    return population_with_fitness



def mutate_child(child, params):

    mutated_child = []
    for gene_cluster_id in range(len(child)):
        gene_cluster = []
        for gene_id, gene_type in enumerate(WireGene):
            if random.random() < params["mutation_rate"]:
                gene_cluster.append(random_gene(gene_cluster_id, gene_type, params))
            else:
                gene_cluster.append(child[gene_cluster_id][gene_id])
        mutated_child.append(tuple(gene_cluster))
    return mutated_child



def next_generation(population, params):
    new_population = []

    population_with_scores = [(chromosome, score) for chromosome, score in sorted(calculate_fitness(population, params), key=lambda x: x[1])]

    for i in range(int(params["population_size"]/2)):
        # pick candidates
        candidate11 = random.choice(population_with_scores)
        candidate12 = random.choice(population_with_scores)
        candidate21 = random.choice(population_with_scores)
        candidate22 = random.choice(population_with_scores)
        
        # challenge
        parent1 = candidate11[0] if candidate11[1] > candidate12[1] else candidate12[0]
        parent2 = candidate21[0] if candidate21[1] > candidate22[1] else candidate22[0]

        # crossover
        chromosome_length = len(parent1[0])
        if random.uniform(0, 1) < params["crossover_rate"]:
            crossover_point = random.randint(1, chromosome_length-1)
            child1_unmutated = parent1[:crossover_point] + parent2[crossover_point:]
            child2_unmutated = parent2[:crossover_point] + parent1[crossover_point:]
        else:
            child1_unmutated = parent1
            child2_unmutated = parent2

        # mutate
        child1 = mutate_child(child1_unmutated, params)
        child2 = mutate_child(child2_unmutated, params)

        new_population.append(child1)
        new_population.append(child2)

    if len(new_population) < params["population_size"]:
        # fill in the best
        new_population.append(population_with_scores[0][0])

    if not (len(new_population) == params["population_size"]):
        raise("At this point new_population is expected to be complete, but is not: new population size: {len(new_population)}, expected: {params['population_size']}")

    return new_population



def plot_scores(scores):

    for generation, scores in enumerate(scores):
        for score in scores:
            plt.scatter(generation, score)

    plt.show()



if __name__ == "__main__":

    params = {"freq": 433.0,
              "wire_len_limits": (0.005, 0.4), # [m]
              "distance_step": 0.005, # [m]
              "max_distance_steps": 80,
              "num_elements": 7,
              "population_size": 100,
              "crossover_rate": 0.5,
              "mutation_rate": 0.05,
              "num_generations": 100,
              "fitness_scores_file": "fitness_scores.json", 
              "last_generation_file": "last_generation.txt"}

    scores = []

    # Initialization
    population = initialize_population(params)
    scores.append([score for chromosome, score in calculate_fitness(population, params)])
    print("\nInitial:")
    print(calculate_fitness(population, params))

    # Run evolution
    for gen_id in range(1, params["num_generations"]+1):

        population = next_generation(population, params)
        scores.append([score for chromosome, score in calculate_fitness(population, params)])
        print(f"\nGeneration {gen_id}:")
        print(calculate_fitness(population, params))

    with open(params["last_generation_file"], 'w') as f:
        f.write(str(sorted(calculate_fitness(population, params), key=lambda x: x[1])))


    # Visualize data at the end
    plot_scores(scores)
