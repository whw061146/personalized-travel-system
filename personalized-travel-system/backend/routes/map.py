from flask import Blueprint, request, jsonify
from backend.models import db, Place, Route
import networkx as nx

map_bp = Blueprint('map', __name__)

# 创建图结构存储路径信息
graph = nx.DiGraph()

def initialize_graph():
    routes = Route.query.all()
    for route in routes:
        graph.add_edge(route.start_place_id, route.end_place_id, weight=route.distance)

# 计算最短路径（Dijkstra）
@map_bp.route('/shortest-path', methods=['GET'])
def shortest_path():
    start_id = request.args.get('start_id', type=int)
    end_id = request.args.get('end_id', type=int)
    
    if not start_id or not end_id:
        return jsonify({'error': '必须提供起点和终点 ID'}), 400
    
    if start_id not in graph.nodes or end_id not in graph.nodes:
        return jsonify({'error': '起点或终点不存在'}), 404
    
    try:
        path = nx.shortest_path(graph, source=start_id, target=end_id, weight='weight')
        return jsonify({'shortest_path': path}), 200
    except nx.NetworkXNoPath:
        return jsonify({'error': '无可达路径'}), 400

# 计算多目标最优路径（TSP 旅行商问题）
@map_bp.route('/tsp-route', methods=['POST'])
def tsp_route():
    data = request.get_json()
    places = data.get('places', [])  # 需要经过的地点 ID 列表
    
    if not places or len(places) < 2:
        return jsonify({'error': '至少提供两个地点'}), 400
    
    # 生成最优旅行路径
    subgraph = graph.subgraph(places)
    tsp_path = nx.approximation.traveling_salesman_problem(subgraph, cycle=False)
    
    return jsonify({'optimized_route': tsp_path}), 200

# 初始化图结构
with db.app.app_context():
    initialize_graph()
