import math
import random

# Função para ler instâncias de um arquivo
def read_instances(filename="zoo.txt"):
    """Lê instâncias de um ficheiro e devolve-as numa lista, sem o nome do animal."""
    instances = []
    try:
        with open(filename, "r") as file:
            for line in file:
                instance = line.strip().strip("[]").split(",")
                instance = [int(x) if i < 16 else x.strip() for i, x in enumerate(instance[1:])]
                instances.append(instance)
    except FileNotFoundError:
        print(f"Erro: Arquivo {filename} não encontrado.")
        return []
    return instances

#Classe para representar o nó da árvore de decisão
class Node:
  def __init__(self, value="", name="", instances=None, branches=None):
      self.value = value
      self.name = name
      self.instances = instances if instances is not None else []
      self.branches = branches if branches is not None else []

#Função para contar o número de instâncias de cada classe
def count_classes(instances, classes):
  class_counts = [[class_name, 0] for class_name in classes]
  for instance in instances:
    class_name = instance[-1]
    if class_name not in class_counts:
      class_counts[class_name] = 0
    class_counts[class_name] += 1
  return class_counts

# Função para escolher o melhor atributo
def _choose_attr(instances, attributes, classes):
    min_entropy = 100
    best_attr = -1
    for i in range(len(attributes)):  # para cada atributo
        instance_sets = []
        total_entropy = 0
        for j in range(len(attributes[i][1])):  # para cada valor do atributo
            # vai buscar as instancias com esse valor do atributo
            insts = [inst for inst in instances if inst[i] == attributes[i][1][j]] #Aqui mudei inst[i+1] para inst[i]
            counts = count_classes(insts, classes)  # Retorna [[classe, contador], ...]
            entropy = 0
            size = len(insts)
            for c in counts:  # Itera sobre [[classe, contador], ...]
                if c[1] > 0:
                    entropy = entropy - c[1] / size * math.log2(c[1] / size)
            total_entropy = total_entropy + size / len(instances) * entropy  # entropia total do atributo
        if min_entropy > total_entropy:
            min_entropy = total_entropy
            best_attr = i
    return best_attr

#Função para construir a árvore ID3
def build(instances, attributes, classes, value, default):
    #casos de paragem
    if not instances:  
        #já não há instâncias
        return Node(name=default)  
    elif not attributes:  
        #já não há atributos
        counts = count_classes(instances, classes)
        majority = max(counts, key=lambda x: x[1])[0]  
        return Node(name=majority)  
    elif len(set(inst[-1] for inst in instances)) == 1:  
        return Node(name=instances[0][-1]) 
    #caso geral
    else:
        best_attribute = _choose_attr(None, instances, attributes, classes)  # Ajuste: passa None para self
        new_attributes = attributes[:best_attribute] + attributes[best_attribute + 1:] 
        branches = []  
        for value in attributes[best_attribute][1]: 
            #criar cada ramo
            new_instances = [inst for inst in instances if inst[best_attribute] == value] 
            counts = count_classes(instances, classes)
            majority = max(counts, key=lambda x: x[1])[0] 
            new_branch = build(new_instances, new_attributes, classes, value, majority) 
            branches.append(new_branch) 
        return Node(value=value, name=best_attribute, instances=instances, branches=branches) 

#Função para imprimir a árvore de decisão
def print_tree(node, level=0):
    indent = "  " * level
    if not node.branches:
        print(f"{indent}{node.name}")
    else:
        print(f"{indent}{node.name} = {node.value}:")
        for branch in node.branches:
            print_tree(branch, level + 1)

# Função para classificar uma instância
def classify(tree, instance, attributes):
    node = tree
    while node.branches:
        attr_idx = next(i for i, attr in enumerate(attributes[:-1]) if attr[0] == node.name)
        value = instance[attr_idx]
        node = next(b for b in node.branches if b.value == value)
    return node.name

#Função para testar a precisão do classificador
def test_precision(instances, attributes, classes):
    results = []
    for _ in range(10):
        shuffled = instances.copy()
        random.shuffle(shuffled)
        test_size = len(shuffled) // 10
        test_set = shuffled[:test_size]
        train_set = shuffled[test_size:]
        tree = build(train_set, attributes, classes)
        success = sum(1 for inst in test_set if classify(tree, inst, attributes) == inst[-1])
        results.append(success / len(test_set))
    mean = sum(results) / len(results)
    std_dev = (sum((x - mean) ** 2 for x in results) / len(results)) ** 0.5
    return results, mean, std_dev

#Função Principal do programa
def main():
  concept = "animal type"
  attributes = [["hair", [0, 1]],
    ["feathers", [0, 1]],
    ["eggs", [0, 1]],
    ["milk", [0, 1]],
    ["airborne" , [0, 1]],
    ["aquatic" , [0, 1]],
    ["predator" , [0, 1]],
    ["toothed" , [0, 1]],
    ["backbone" , [0, 1]],
    ["breathes" , [0, 1]],
    ["venomous" , [0, 1]],
    ["fins" , [0, 1]],
    ["legs" , [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]],
    ["tail" , [0, 1]],
    ["domestic" , [0, 1]],
    ["catsize" , [0, 1]],
    ["class" , ["mammal", "bird", "reptile", "fish", "amphibian", "insect", "invertebrate"]]]
  
  # Ler instâncias do arquivo zoo.txt
  instances = read_instances("zoo.txt")
  """id3 = ID3(concept, instances, attributes)
  id3.run()"""

  classes = attributes[-1][1]
    
  # Construir e imprimir a árvore com todas as instâncias
  tree = build(instances, attributes, classes, value="", default=None)
  print("Árvore de decisão:")
  print_tree(tree)
    
  # Exemplo de classificação (aardvark)
  aardvark = [1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 4, 0, 0, 1, "mammal"]
  pred = classify(tree, aardvark, attributes)
  print(f"\naardvark is a {aardvark[-1]} and is classified as a {pred}")
    
  # Teste de precisão
  results, mean, std_dev = test_precision(instances, attributes, classes)
  print("\nResultados de precisão (10 iterações):")
  for i, res in enumerate(results, 1):
      print(f"Iteração {i}: {res:.2%}")
  print(f"Precisão média: {mean:.2%}")
  print(f"Desvio padrão: {std_dev:.4f}")

if __name__ == "__main__":
    main()