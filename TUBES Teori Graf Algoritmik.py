'''
Tugas Besar Teori Graf Algoritmik
10620002 - Dzakwanil Hakim
10023578 - Rido Evendi Tarigan
10023499 - Michel Angelica Simanjuntak
'''
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

font_size = 5

def divide_equal_parts(dividend, divisor):
    quotient = dividend // divisor
    remainder = dividend % divisor
    equal_parts = [quotient] * (divisor - remainder) + [quotient + 1] * remainder
    equal_parts.sort(reverse=True)
    return equal_parts

def generate_cycle_permutation_cubic_graphs(n):
    cycle_A = nx.cycle_graph(n)
    cycle_B = nx.cycle_graph(n)
    mapping = {node: node + n for node in cycle_B.nodes()}
    cycle_B = nx.relabel_nodes(cycle_B, mapping)
    nodes_B = list(range(n, 2 * n))
    permutations_B = [nodes_B] + [random.sample(nodes_B, len(nodes_B)) for _ in range(3)]
    graphs = []
    for permuted_nodes_B in permutations_B:
        combined_graph = nx.compose(cycle_A, cycle_B)
        for i in range(n):
            combined_graph.add_edge(i, permuted_nodes_B[i], weight=0)
        graphs.append(combined_graph)
    return graphs

def bfs_node_labels(graph, start_node):
    bfs_order = list(nx.bfs_edges(graph, start_node))
    labels = {start_node: 0}
    current_label = 1
    for edge in bfs_order:
        for node in edge:
            if node not in labels:
                labels[node] = current_label
                current_label += 1
    labels = {node: label + 4 for node, label in labels.items()}
    return labels

def assign_weights(graph, start_node):
    node_labels = bfs_node_labels(graph, start_node)
    for node in graph.nodes():
        graph.nodes[node]['weight'] = 0
    for edge in graph.edges():
        graph.edges[edge]['weight'] = 0
    node_weights = {}
    edge_weights = {}
    for node, label in node_labels.items():
        zero_edges = [(u, v) for u, v in graph.edges(node) if graph[u][v].get('weight', 0) == 0]
        non_zero_edges = [(u, v) for u, v in graph.edges(node) if graph[u][v].get('weight', 0) != 0]
        zero_edges.sort(key=lambda x: x[1], reverse=True)
        weight_start = label - sum(graph[u][v].get('weight', 0) for u, v in non_zero_edges)
        count_edge_zero = len(zero_edges)
        weight_parts = divide_equal_parts(weight_start, count_edge_zero + 1)
        for edge in zero_edges:
            graph.edges[edge]['weight'] = weight_parts[0]
            weight_parts.pop(0)
        graph.nodes[node]['weight'] = weight_parts[0]
        node_weights[node] = graph.nodes[node]['weight']
        for edge in zero_edges:
            edge_weights[edge] = graph.edges[edge]['weight']
    return node_weights, edge_weights

def visualize_graph(graph, node_labels, node_weights, edge_weights, ax, seed=42, highlight_edges=None):
    n = len(node_labels) // 2  # Assuming the graph is composed of two cycles of length n each
    pos_A = nx.circular_layout(range(n))
    pos_B = nx.circular_layout(range(n, 2 * n))
    
    # Scale positions for the inner cycle
    for key in pos_B:
        pos_B[key] *= 0.5
    
    # Combine positions
    pos = {**pos_A, **pos_B}
    
    # Create labels dictionary including the original labels
    labels = {node: f"{node_weights[node]}, ({node_labels[node]}), [{node}]" for node in graph.nodes()}
    
    # Reduced node size and font size
    nx.draw(graph, pos, with_labels=False, node_color='skyblue', node_size=500, edge_color='gray', ax=ax)
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=font_size, font_color='green', font_weight='bold', ax=ax)
    
    # Draw edge labels with green font color
    for edge, weight in edge_weights.items():
        nx.draw_networkx_edge_labels(graph, pos, edge_labels={(edge[0], edge[1]): weight}, font_color='green', font_size=8, ax=ax)

    # Highlight the specified edges if provided
    if highlight_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=highlight_edges, edge_color='red', width=2.5, ax=ax)

    # Add custom legend as a text annotation
    legend_text = "Nodes legend:\nx, (y), [z] : x label node, y weight node, z original label"
    ax.text(0.05, 0.95, legend_text, transform=ax.transAxes, fontsize=5,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))

    ax.axis('off')

def graph_info(node_labels, node_weights, edge_weights, count_base_node):
    info = "(Node weight, Node label):\n"
    for node, label in node_labels.items():
        info += f"{label}: {node_weights[node]}\n"
    info += "\nEdge label:\n"
    for edge, weight in edge_weights.items():
        info += f"{edge}: {weight}\n"
    max_weight = max(max(node_weights.values()), max(edge_weights.values()))
    tvs_theory = math.ceil((count_base_node * 2 + 3) / 4)
    info += f"\nActual TVS: {max_weight}\nPrediction TVS: {tvs_theory}\n"
    return info

def generate_output(graphs, n, to_file=False):
    output = ""
    for i, graph in enumerate(graphs):
        if i == 0:
            output += f"\nCubic graph without permutation\n"
        else:
            output += f"\nCubic graph permutation {i}\n"
        start_node = 0
        node_labels = bfs_node_labels(graph, start_node)
        node_weights, edge_weights = assign_weights(graph, start_node)
        output += graph_info(node_labels, node_weights, edge_weights, n)
        output += '\n' + '='*64 + '\n'
    if to_file:
        return output
    else:
        return output

def visualize_graphs(graphs, n, root):
    # Create a new window for the visualizations
    window = tk.Toplevel(root)
    window.title("Graph Visualizations")
    
    # Create a notebook to hold the tabs
    notebook = ttk.Notebook(window)
    notebook.pack(fill='both', expand=True)
    
    # Create a figure for each graph and add it to a tab
    for i, graph in enumerate(graphs):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=f"Graph {i+1}")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        start_node = 0
        node_labels = bfs_node_labels(graph, start_node)
        node_weights, edge_weights = assign_weights(graph, start_node)
        visualize_graph(graph, node_labels, node_weights, edge_weights, ax=ax, seed=42)
        ax.set_title(f"Cubic graph permutation {i}" if i > 0 else "Cubic graph without permutation")
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

def export_to_txt(file_path, graphs, n):
    output = generate_output(graphs, n, to_file=True)
    with open(file_path, "w") as f:
        f.write(output)
    print(f"Output has been saved to {file_path}")

def run_dijkstra(graph, start_node, end_node):
    path = nx.dijkstra_path(graph, source=start_node, target=end_node, weight='weight')
    path_edges = list(zip(path[:-1], path[1:]))
    return path, path_edges

def run_dfs(graph, start_node, end_node):
    path = list(nx.dfs_edges(graph, source=start_node))
    return path

def run_bfs(graph, start_node, end_node):
    path = list(nx.bfs_edges(graph, source=start_node))
    return path

def run_shortest_cycle(graph):
    try:
        cycle = nx.find_cycle(graph)
        return cycle
    except nx.NetworkXNoCycle:
        return None

def run_kruskal(graph):
    mst = nx.minimum_spanning_tree(graph, algorithm='kruskal')
    return mst.edges(data=True)

def run_prim(graph):
    mst = nx.minimum_spanning_tree(graph, algorithm='prim')
    return mst.edges(data=True)

def find_connected_components(graph):
    components = list(nx.connected_components(graph))
    return components

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("TUBES Teori Graf Algoritmik")
        self.graphs = None

        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Enter the number of base cycle nodes:").pack(padx=5, pady=5)
        self.n_entry = ttk.Entry(frame)
        self.n_entry.pack(padx=5, pady=5)

        self.generate_button = ttk.Button(frame, text="Generate Graphs", command=self.generate_graphs)
        self.generate_button.pack(padx=5, pady=5)

        self.export_button = ttk.Button(frame, text="Export Output", command=self.export_output)
        self.export_button.pack(padx=5, pady=5)

        self.visualize_button = ttk.Button(frame, text="Visualize Graphs", command=self.visualize_graphs)
        self.visualize_button.pack(padx=5, pady=5)

        self.dijkstra_button = ttk.Button(frame, text="Run Dijkstra", command=self.run_dijkstra_ui)
        self.dijkstra_button.pack(padx=5, pady=5)
        
        self.dfs_button = ttk.Button(frame, text="Run DFS", command=self.run_dfs_ui)
        self.dfs_button.pack(padx=5, pady=5)

        self.bfs_button = ttk.Button(frame, text="Run BFS", command=self.run_bfs_ui)
        self.bfs_button.pack(padx=5, pady=5)

        self.shortest_cycle_button = ttk.Button(frame, text="Find Shortest Cycle", command=self.find_shortest_cycle_ui)
        self.shortest_cycle_button.pack(padx=5, pady=5)

        self.kruskal_button = ttk.Button(frame, text="Run Kruskal", command=self.run_kruskal_ui)
        self.kruskal_button.pack(padx=5, pady=5)

        self.prim_button = ttk.Button(frame, text="Run Prim's", command=self.run_prim_ui)
        self.prim_button.pack(padx=5, pady=5)

        self.connected_components_button = ttk.Button(frame, text="Find Connected Components", command=self.find_connected_components_ui)
        self.connected_components_button.pack(padx=5, pady=5)

        self.reset_button = ttk.Button(frame, text="Reset", command=self.reset)
        self.reset_button.pack(padx=5, pady=5)

        self.output_text = ScrolledText(frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def generate_graphs(self):
        try:
            n = int(self.n_entry.get())
            if n <= 0:
                raise ValueError
            self.graphs = generate_cycle_permutation_cubic_graphs(n)
            output = generate_output(self.graphs, n)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output, "tag")
            self.output_text.config(state=tk.DISABLED)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive integer.")

    def export_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            export_to_txt(file_path, self.graphs, int(self.n_entry.get()))
            messagebox.showinfo("Export Successful", f"Output has been saved to {file_path}")

    def visualize_graphs(self):
        if self.graphs is None:
            messagebox.showwarning("Visualization Error", "No graphs to visualize. Please generate graphs first.")
            return
        n = int(self.n_entry.get())
        visualize_graphs(self.graphs, n, self.root)

    def run_dijkstra_ui(self):
        if self.graphs is None:
            messagebox.showwarning("Dijkstra Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Run Dijkstra's Algorithm", self.run_dijkstra_button)

    def run_dfs_ui(self):
        if self.graphs is None:
            messagebox.showwarning("DFS Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Run DFS Algorithm", self.run_dfs_button)

    def run_bfs_ui(self):
        if self.graphs is None:
            messagebox.showwarning("BFS Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Run BFS Algorithm", self.run_bfs_button)

    def find_shortest_cycle_ui(self):
        if self.graphs is None:
            messagebox.showwarning("Cycle Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Find Shortest Cycle", self.run_shortest_cycle_button)

    def run_kruskal_ui(self):
        if self.graphs is None:
            messagebox.showwarning("Kruskal Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Run Kruskal's Algorithm", self.run_kruskal_button)

    def run_prim_ui(self):
        if self.graphs is None:
            messagebox.showwarning("Prim's Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Run Prim's Algorithm", self.run_prim_button)

    def find_connected_components_ui(self):
        if self.graphs is None:
            messagebox.showwarning("Connected Components Error", "No graphs available. Please generate graphs first.")
            return
        self.run_algorithm_ui("Find Connected Components", self.find_connected_components_button)

    def run_algorithm_ui(self, title, command):
        algorithm_window = tk.Toplevel(self.root)
        algorithm_window.title(title)

        ttk.Label(algorithm_window, text="Select Graph:").pack(padx=5, pady=5)
        graph_select = ttk.Combobox(algorithm_window, values=[f"Graph {i+1}" for i in range(len(self.graphs))])
        graph_select.pack(padx=5, pady=5)

        ttk.Label(algorithm_window, text="Start Node:").pack(padx=5, pady=5)
        start_node_entry = ttk.Entry(algorithm_window)
        start_node_entry.pack(padx=5, pady=5)

        end_node_label = ttk.Label(algorithm_window, text="End Node:")
        end_node_entry = ttk.Entry(algorithm_window)

        if title not in ["Find Shortest Cycle", "Run Kruskal's Algorithm", "Run Prim's Algorithm", "Find Connected Components"]:
            end_node_label.pack(padx=5, pady=5)
            end_node_entry.pack(padx=5, pady=5)

        def run_button():
            try:
                graph_idx = int(graph_select.current())
                start_node = int(start_node_entry.get())
                end_node = None if end_node_entry.get() == "" else int(end_node_entry.get())
                graph = self.graphs[graph_idx]
                command(graph, graph_idx, start_node, end_node)
            except Exception as e:
                messagebox.showerror(f"{title} Error", str(e))

        run_button = ttk.Button(algorithm_window, text="Run Algorithm", command=run_button)
        run_button.pack(padx=5, pady=5)

    def run_dijkstra_button(self, graph, graph_idx, start_node, end_node):
        path, path_edges = run_dijkstra(graph, start_node, end_node)
        messagebox.showinfo("Dijkstra Result", f"Shortest path: {path}\nPath length: {len(path)-1}")
        self.visualize_shortest_path(graph_idx, path_edges)

    def run_dfs_button(self, graph, graph_idx, start_node, end_node):
        path = run_dfs(graph, start_node, end_node)
        messagebox.showinfo("DFS Result", f"DFS path: {path}")
        self.visualize_search_path(graph_idx, path)

    def run_bfs_button(self, graph, graph_idx, start_node, end_node):
        path = run_bfs(graph, start_node, end_node)
        messagebox.showinfo("BFS Result", f"BFS path: {path}")
        self.visualize_search_path(graph_idx, path)

    def run_shortest_cycle_button(self, graph, graph_idx, start_node, end_node):
        cycle = run_shortest_cycle(graph)
        if cycle is None:
            messagebox.showinfo("Shortest Cycle Result", "No cycle found.")
        else:
            messagebox.showinfo("Shortest Cycle Result", f"Shortest cycle: {cycle}")
            self.visualize_search_path(graph_idx, cycle)

    def run_kruskal_button(self, graph, graph_idx, start_node, end_node):
        mst_edges = run_kruskal(graph)
        messagebox.showinfo("Kruskal Result", f"Kruskal's MST edges: {mst_edges}")
        self.visualize_search_path(graph_idx, list(mst_edges))

    def run_prim_button(self, graph, graph_idx, start_node, end_node):
        mst_edges = run_prim(graph)
        messagebox.showinfo("Prim's Result", f"Prim's MST edges: {mst_edges}")
        self.visualize_search_path(graph_idx, list(mst_edges))

    def find_connected_components_button(self, graph, graph_idx, start_node, end_node):
        components = find_connected_components(graph)
        messagebox.showinfo("Connected Components Result", f"Connected components: {components}")

    def visualize_shortest_path(self, graph_idx, path_edges):
        window = tk.Toplevel(self.root)
        window.title("Shortest Path Visualization")

        frame = ttk.Frame(window)
        frame.pack(fill='both', expand=True)

        fig, ax = plt.subplots(figsize=(8, 6))
        graph = self.graphs[graph_idx]
        start_node = 0
        node_labels = bfs_node_labels(graph, start_node)
        node_weights, edge_weights = assign_weights(graph, start_node)
        visualize_graph(graph, node_labels, node_weights, edge_weights, ax=ax, seed=42, highlight_edges=path_edges)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def visualize_search_path(self, graph_idx, path):
        window = tk.Toplevel(self.root)
        window.title("Search Path Visualization")

        frame = ttk.Frame(window)
        frame.pack(fill='both', expand=True)

        fig, ax = plt.subplots(figsize=(8, 6))
        graph = self.graphs[graph_idx]
        start_node = 0
        node_labels = bfs_node_labels(graph, start_node)
        node_weights, edge_weights = assign_weights(graph, start_node)
        visualize_graph(graph, node_labels, node_weights, edge_weights, ax=ax, seed=42, highlight_edges=path)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def reset(self):
        self.graphs = None
        self.n_entry.delete(0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
