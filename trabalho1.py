"""
Autor: Joseanne Gourgel
Nº: 20230253
Descrição:Trabalho 1 - Algoritmos de Aprendizagem
"""

import math
import random
import statistics

# --- Definição dos atributos e classes ---
attributes = [
    ["hair", [0, 1]],
    ["feathers", [0, 1]],
    ["eggs", [0, 1]],
    ["milk", [0, 1]],
    ["airborne", [0, 1]],
    ["aquatic", [0, 1]],
    ["predator", [0, 1]],
    ["toothed", [0, 1]],
    ["backbone", [0, 1]],
    ["breathes", [0, 1]],
    ["venomous", [0, 1]],
    ["fins", [0, 1]],
    ["legs", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]],  # 0 a 9 pernas
    ["tail", [0, 1]],
    ["domestic", [0, 1]],
    ["catsize", [0, 1]],
]

classes = ["mammal", "bird", "reptile", "fish", "amphibian", "insect", "invertebrate"]


# --- Classe Node ---
class Node:
    def __init__(self, value="", name="", instances=None):
        self.value = value            # valor do ramo que chega neste nó
        self.name = name              # nome do atributo ou classe 
        self.instances = instances if instances else []
        self.branches = []            # lista de nós filhos

    def add_branch(self, node):
        self.branches.append(node)

# --- Função para ler as instâncias ---
def read_instances(filename):
    instances = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip().strip("[]")
            parts = line.split(",")
            name = parts[0]
            attributes = [int(x) for x in parts[1:-1]]
            classification = parts[-1]
            instance = [name] + attributes + [classification]
            instances.append(instance)
    return instances

# --- Contar instâncias por classe ---
def count_classes(instances, classes):
    counts = []
    for c in classes:
        n = sum(1 for inst in instances if inst[-1] == c)
        counts.append([c, n])
    return counts

# --- Escolher o melhor atributo (ID3) ---
def choose_attr(instances, attributes, classes):
    min_entropy = 100
    best_attr = -1

    for i in range(len(attributes)):
        total_entropy = 0
        for val in attributes[i][1]:
            subset = [inst for inst in instances if inst[i+1] == val]  # +1 para poder ignorar o nome
            size = len(subset)
            if size == 0:
                continue
            counts = count_classes(subset, classes)
            entropy = 0
            for c, count in counts:
                if count > 0:
                    p = count / size
                    entropy -= p * math.log2(p)
            total_entropy += (size / len(instances)) * entropy
        if total_entropy < min_entropy:
            min_entropy = total_entropy
            best_attr = i
    return best_attr

# --- Construir árvore recursivamente ---
def build(instances, attributes, classes, value="", default_class=None):
    if not instances:
        return Node(value=value, name=default_class)
    class_counts = count_classes(instances, classes)
    max_count = max(class_counts, key=lambda x: x[1])[1]
    majority_class = max(class_counts, key=lambda x: x[1])[0]

    # Caso 2: Se todas as instâncias têm a mesma classe
    if max_count == len(instances):
        return Node(value=value, name=instances[0][-1])

    # Caso 3: Se não há atributos para dividir
    if not attributes:
        return Node(value=value, name=majority_class)

    best_attr_index = choose_attr(instances, attributes, classes)
    best_attr = attributes[best_attr_index]

    root = Node(value=value, name=best_attr[0], instances=instances)

    new_attributes = attributes[:best_attr_index] + attributes[best_attr_index+1:]

    for val in best_attr[1]:
        subset = [inst for inst in instances if inst[best_attr_index + 1] == val]
        branch = build(subset, new_attributes, classes, value=val, default_class=majority_class)
        root.add_branch(branch)

    return root

# --- Imprimir árvore ---
def print_tree(node, level=0):
    indent = "  " * level
    if not node.branches:  # folha
        print(f"{indent}{node.value}: {node.name}")
    else:
        for branch in node.branches:
            print(f"{indent}{node.name} = {branch.value}:")
            print_tree(branch, level + 1)

# --- Classificar instância ---
def classify(node, instance):
    if not node.branches:
        return node.name  # folha
    attr_index = None
    for i, attr in enumerate(attributes):
        if attr[0] == node.name:
            attr_index = i + 1  # +1 para ignorar o nome
            break
    if attr_index is None:
        return None
    attr_value = instance[attr_index]
    for branch in node.branches:
        if branch.value == attr_value:
            return classify(branch, instance)
    return None

# --- Função principal ---
def main():
    file_path = "zoo.txt"
    instances = read_instances(file_path)

    tree = build(instances, attributes, classes)

    print("Árvore de Decisão construída:")
    print_tree(tree)

    # Testar uma instância
    test_inst = instances[0] 
    result = classify(tree, test_inst)
    print(f"\nTeste de classificação para '{test_inst[0]}':")
    print(f" {test_inst[0]} is a {test_inst [-1]} and is classified as a {result}")

    # Avaliar precisão com uma validação cruzada simples
    precisions = []
    for _ in range(10):
        random.shuffle(instances)
        n = len(instances)
        train_set = instances[:int(0.9*n)]
        test_set = instances[int(0.9*n):]

        tree_cv = build(train_set, attributes, classes)

        correct = 0
        for inst in test_set:
            pred = classify(tree_cv, inst)
            if pred == inst[-1]:
                correct += 1
        precision = correct / len(test_set)
        precisions.append(precision)
        print(f"Precisão neste fold: {precision:.3f}")

    avg_precision = sum(precisions) / len(precisions)
    std_dev = statistics.stdev(precisions)
    print(f"\nPrecisão média: {avg_precision:.3f} ± {std_dev:.3f}")

if __name__ == "__main__":
    main()
