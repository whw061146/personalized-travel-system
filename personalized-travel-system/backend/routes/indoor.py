from flask import Blueprint, request, jsonify
from backend.models import db, Facility
import networkx as nx

indoor_bp = Blueprint('indoor', __name__)

# 创建图结构存储室内路径
graph = nx.DiGraph()

def initialize_indoor_graph():
    facilities = Facility.query.all()
    for facility in facilities:
        graph.add_node(facility.id, name=facility.name)
    
    # 这里可以手动添加楼层连接、电梯、楼梯等
    graph.add_edge(1, 2, weight=5)  # 假设 1 到 2 需要 5 秒
    graph.add_edge(2, 3, weight=3)  # 假设 2 到 3 需要 3 秒

# 计算室内最短路径（Dijkstra）
@indoor_bp.route('/indoor-path', methods=['GET'])
def indoor_path():
    start_id = request.args.get('start_id', type=int)
    end_id = request.args.get('end_id', type=int)
    
    if not start_id or not end_id:
        return jsonify({'error': '必须提供起点和终点 ID'}), 400
    
    if start_id not in graph.nodes or end_id not in graph.nodes:
        return jsonify({'error': '起点或终点不存在'}), 404
    
    try:
        path = nx.shortest_path(graph, source=start_id, target=end_id, weight='weight')
        return jsonify({'indoor_path': path}), 200
    except nx.NetworkXNoPath:
        return jsonify({'error': '无可达路径'}), 400

# 初始化室内导航图
with db.app.app_context():
    initialize_indoor_graph()
