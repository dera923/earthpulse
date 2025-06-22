# 🔁 predict_to_dag.py
# /predict API の結果を受け取って、DAGノードとして記録・可視化のために使うユーティリティ

import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

# DAG初期化
G = nx.DiGraph()

# ノード追加関数（場所＋予測）
def add_predict_node(place: str, prediction: str, confidence: float, timestamp: str = None):
    dt = timestamp if timestamp else datetime.now().strftime("%Y%m%d%H%M")
    node_name = f"{place}_{prediction}_{dt}"
    G.add_node(node_name, confidence=confidence, timestamp=timestamp)
    print(f"[+] ノード追加: {node_name}")
    return node_name

# エッジ追加（因果関係）
def add_predict_edge(cause: str, effect: str, confidence: float):
    G.add_edge(cause, effect, weight=confidence)
    print(f"[+] エッジ追加: {cause} → {effect} (信頼度: {confidence})")

# DAGの保存版可視化
def visualize_predict_dag():
    pos = nx.spring_layout(G)
    edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, node_color='lightyellow', node_size=2500, font_size=10, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='gray')

    plt.title("/predict DAG 可視化")
    plt.tight_layout()
    plt.savefig("dag_predict_output.png")
    print("[✓] 画像として保存しました: dag_predict_output.png")

# ✅ テスト実行（単体テスト）
if __name__ == "__main__":
    n1 = add_predict_node("Tokyo", "通信遮断の可能性: 高", 0.85, "202506141336")
    n2 = add_predict_node("Osaka", "影響小", 0.30, "202506141321")
    add_predict_edge(n1, n2, 0.3)
    visualize_predict_dag()
