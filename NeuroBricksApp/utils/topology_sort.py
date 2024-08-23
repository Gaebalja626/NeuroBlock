
from collections import deque, defaultdict

def topological_sort_with_levels(graph):
    """
    위상 정렬 알고리즘

    Description:
        주어진 그래프를 위상 정렬하여 레벨별로 정리합니다.

    :param graph: dict, key: node, value: list of neighbors
    :return: dict, key: level, value: list of nodes
    """
    # 각 노드의 진입 차수를 계산
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    # 진입 차수가 0인 노드를 큐에 삽입
    queue = deque([node for node in in_degree if in_degree[node] == 0])
    levels = defaultdict(list)
    level = 0

    while queue:
        next_queue = deque()
        while queue:
            current = queue.popleft()
            levels[level].append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)
        queue = next_queue
        level += 1

    # 그래프에 사이클이 있는 경우
    if sum(len(nodes) for nodes in levels.values()) != len(graph):
        raise Exception("Graph has at least one cycle")

    return levels