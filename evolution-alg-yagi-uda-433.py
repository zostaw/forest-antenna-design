import necpp
import random
from enum import Enum
import matplotlib.pyplot as plt

def handle_nec(result):
    if (result != 0):
        print(necpp.nec_error_message())

def calc_yagi_impedance(freq, chromosome):

    segments = 21
    height = 10.2
    wire_thickness = 2.55e-4

    # Respect minimal distance
    for id in range(len(chromosome)-1):
        for id2 in range(id+1, len(chromosome)):
            # soft exception if they are both active
            if chromosome[id][0] and chromosome[id2][0] and (abs(chromosome[id][1] - chromosome[id2][1]) < 0.005):
                return 0.0


    
    nec = necpp.nec_create()
    handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[0][2]/2, height, 0, chromosome[0][2]/2, height, 0, wire_thickness, 1, 1))

    if (len(chromosome) > 0) and chromosome[1][0]:
        handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[1][2]/2, height, -chromosome[1][1], chromosome[1][2]/2, height, -chromosome[1][1], wire_thickness, 1, 1))
    if (len(chromosome) > 1):
        for director in chromosome[2:]:
            if director[0]:
                handle_nec(necpp.nec_wire(nec, 1, segments, -director[2]/2, height, director[1], director[2]/2, height, director[1], wire_thickness, 1, 1))

    handle_nec(necpp.nec_geometry_complete(nec, 0))
    handle_nec(necpp.nec_fr_card(nec, 0, 1, freq, 0))
    handle_nec(necpp.nec_ex_card(nec, 0, 1, 11, 1, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)) 
    handle_nec(necpp.nec_rp_card(nec, 0, 360, 1000, 0, 0, 0, 0, 90.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 1, 1000, 0, 0, 0, 0, -90.0, 0.0, 0.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 91, 120, 0, 0, 0, 0, 0.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    result_index = 0
    
    z = complex(necpp.nec_impedance_real(nec,result_index), 
                necpp.nec_impedance_imag(nec,result_index))
    
    necpp.nec_delete(nec)

    return z

def calc_yagi_gain(freq, chromosome):

    segments = 21
    height = 10.2
    wire_thickness = 2.55e-4

    if not chromosome[0][0]:
        return 0.0
    
    nec = necpp.nec_create()
    handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[0][2]/2, height, 0, chromosome[0][2]/2, height, 0, wire_thickness, 1, 1))

    if (len(chromosome) > 0) and chromosome[1][0]:
        handle_nec(necpp.nec_wire(nec, 1, segments, -chromosome[1][2]/2, height, -chromosome[1][1], chromosome[1][2]/2, height, -chromosome[1][1], wire_thickness, 1, 1))
    if (len(chromosome) > 1):
        for director in chromosome[2:]:
            if director[0]:
                handle_nec(necpp.nec_wire(nec, 1, segments, -director[2]/2, height, director[1], director[2]/2, height, director[1], wire_thickness, 1, 1))

    handle_nec(necpp.nec_geometry_complete(nec, 0))
    handle_nec(necpp.nec_fr_card(nec, 0, 1, freq, 0))
    handle_nec(necpp.nec_ex_card(nec, 0, 1, 11, 1, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)) 
    handle_nec(necpp.nec_rp_card(nec, 0, 360, 1000, 0, 0, 0, 0, 90.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 1, 1000, 0, 0, 0, 0, -90.0, 0.0, 0.0, 1.0, 5000.0, 0.0))
    handle_nec(necpp.nec_rp_card(nec, 0, 91, 120, 0, 0, 0, 0, 0.0, 0.0, 1.0, 1.0, 5000.0, 0.0))
    result_index = 0
    
    g = necpp.nec_gain_max(nec, 0)
    
    necpp.nec_delete(nec)

    return g

WireGene = Enum('WireGene', [('EXISTANCE', 0), ('DISTANCE', 1), ('LENGTH', 2)])

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

def calculate_fitness(population, params, scores_list={}):
    population_with_fitness = []
    for chromosome in population:
        if not str(chromosome) in scores_list.keys():
            try:
                score = calc_yagi_gain(params["freq"], chromosome)
            except:
                score = 0.0
            finally:
                scores_list[str(chromosome)] = score


        population_with_fitness.append((chromosome, scores_list[str(chromosome)]))
    
    return population_with_fitness

def selection(population, params):
    return [chromosome for chromosome, score in sorted(calculate_fitness(population, params), key=lambda x: x[1])[int(params["best_ratio"]*len(population)):]]

def crossover(selected, population, params):
    chromosome_length = len(population[0])
    offspring_cross = []
    for i in range(params["population_size"]):
        parent1 = list(random.choice(selected))
        parent2 = list(random.choice(population))

        crossover_point = random.randint(1, chromosome_length-1)

        child = parent1[:crossover_point] + parent2[crossover_point:]
        offspring_cross.append(child)
    
    return offspring_cross

def mutate(crossovered, params):
    mutated_offspring = []

    for chromosome in crossovered:
        mutated_chromosome = []
        for gene_cluster_id in range(len(chromosome)):
            gene_cluster = []
            for gene_id, gene_type in enumerate(WireGene):
                if random.random() < params["mutation_rate"]:
                    gene_cluster.append(random_gene(gene_cluster_id, gene_type, params))
                else:
                    gene_cluster.append(chromosome[gene_cluster_id][gene_id])
            mutated_chromosome.append(tuple(gene_cluster))
        mutated_offspring.append(mutated_chromosome)

    return mutated_offspring

def next_generation(population, params):
    return mutate(crossover(selection(population, params), population, params), params)


def plot_scores(scores):

    for generation, scores in enumerate(scores):
        for score in scores:
            plt.scatter(generation, score)

    plt.show()

"""
Gene: number/boolean
Chromosome: [dipole, reflector, director1, director2, ...] where each dipole/reflector/director is set of (existance, distance, length) - for dipole existance and distance are ignored

Criteria:
1. if directors are too close to each other - the chromosome dies
2. wire lengths only within limit
"""


if __name__ == "__main__":

    params = {"freq": 433.0,
              "wire_len_limits": (0.005, 0.3), # [m]
              "distance_step": 0.005, # [m]
              "max_distance_steps": 200,
              "num_elements": 6,
              "population_size": 16,
              "best_ratio": 0.5,
              "mutation_rate": 0.1,
              "num_generations": 40}

    scores = []

    # Initialization
    population = initialize_population(params)
    scores.append([score for chromosome, score in calculate_fitness(population, params)])
    print("\nInitial:")
    for chromosome, score in calculate_fitness(population, params):
        print(f"Chromosome \t {chromosome}")
        print(f"Score \t {score}")

    # # Selection
    # selected = selection(population, params)
    # print("\nSelected:")
    # for chromosome, score in calculate_fitness(selected, params):
    #     print(f"Chromosome \t {chromosome}")
    #     print(f"Score \t {score}")


    # # Crossover
    # crossovered = crossover(selected, population, params)
    # print("\nCrossovered:")
    # for chromosome, score in calculate_fitness(crossovered, params):
    #     print(f"Chromosome \t {chromosome}")
    #     print(f"Score \t {score}")

    # # Mutation
    # mutated = mutate(crossovered, params)
    # scores.append([score for chromosome, score in calculate_fitness(mutated, params)])
    # print("\nMutated:")
    # for chromosome, score in calculate_fitness(mutated, params):
    #     print(f"Chromosome \t {chromosome}")
    #     print(f"Score \t {score}")

    for gen_id in range(1, params["num_generations"]+1):
        next_gen = next_generation(population, params)
        scores.append([score for chromosome, score in calculate_fitness(next_gen, params)])
        print(f"\nGeneration {gen_id}:")
        for chromosome, score in calculate_fitness(next_gen, params):
            print(f"Chromosome \t {chromosome}")
            print(f"Score \t {score}")


    plot_scores(scores)
