
import json
import graphviz
import os

def generate_codex_graph(codex_path="registry/codex.json", output_path="codex_map"):
    print(f"🕸️ Mapping Citadel Logic from {codex_path}...")
    
    if not os.path.exists(codex_path):
        print("❌ Codex missing.")
        return

    with open(codex_path, "r") as f:
        data = json.load(f)

    dot = graphviz.Digraph('Citadel_Strategies', comment='T.I.A. Strategy Map')
    dot.attr(rankdir='LR', bgcolor='#0f0c29')
    dot.attr('node', shape='box', style='filled', fontname='Courier New', fontcolor='white')

    # Engines
    with dot.subgraph(name='cluster_engines') as c:
        c.attr(label='Execution Engines', color='white', fontcolor='white')
        c.attr('node', fillcolor='#302b63', color='#00ffcc')
        for eng in data['engines']:
            c.node(f"ENG_{eng['id']}", eng['name'])

    # Overlays
    with dot.subgraph(name='cluster_overlays') as c:
        c.attr(label='Risk Overlays', color='white', fontcolor='white')
        c.attr('node', fillcolor='#800020', color='#ff0000')
        for ov in data['overlays']:
            c.node(f"OV_{ov['id']}", ov['name'])

    # Strategies
    for strat in data['strategies'].values(): # It's a dict now in registry, but json is list. 
        # Handle both list and dict format just in case
        s_id = strat['id']
        s_name = strat['name']
        s_fam = strat['family']
        
        color = '#228b22' if s_fam == 'trend' else '#ff8c00'
        dot.node(f"STR_{s_id}", s_name, fillcolor=color, color='white')

        # Edges would go here if we defined explicit links in JSON
        # For now, linking everything to the default engine for visualization
        dot.edge("ENG_eng_vortex_v1", f"STR_{s_id}", color='#555555')

    try:
        output_file = dot.render(output_path, format='png', cleanup=True)
        print(f"✅ Visual Graph Generated: {output_file}")
    except Exception as e:
        print(f"⚠️ Graphviz Error (check system install): {e}")

if __name__ == "__main__":
    generate_codex_graph()
