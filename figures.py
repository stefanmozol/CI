#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Get current directory where script is located
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
if OUTPUT_DIR == '':
    OUTPUT_DIR = '.'



DATA_TOPOLOGY = {
    'loads': ['LOW', 'MEDIUM', 'HIGH'],
    'dml': {
        'mean': [91.8, 680.5, 1072.6],
        'std': [18.6, 48.5, 35.7]
    },
    'ci': {
        'mean': [67.4, 72.3, 80.2],
        'std': [0.9, 0.7, 2.0]
    },
    'hybrid': {
        'mean': [68.0, 71.3, 81.5],
        'std': [1.0, 0.8, 1.1]
    },
    'improvement': ['+26.6%', '+89.4%', '+92.5%']
}


DATA_RULES = {
    'rules': ['STT', 'SPT', 'SQ', 'NA', 'LB'],
    'throughput_time': {
        'mean': [72.3, 91.0, 92.4, 144.7, 677.7],
        'std': [0.7, 1.6, 1.8, 3.1, 47.1]
    },
    'queue_time': [8.5, 19.4, 18.7, 29.0, 136.3],
    'transport_time': [11.5, 12.1, 13.2, 9.8, 18.4],
    'utilization': [22.9, 22.4, 23.5, 23.2, 17.4],
    'improvement_vs_dml': ['+89.4%', '+86.6%', '+86.4%', '+78.7%', '−0.4%'],
    'dml_baseline': 680.5
}


DATA_BREAKDOWN = {
    'configs': ['DML', 'CI+STT', 'CI+SQ', 'CI+LB', 'HYBRID'],
    'processing': [47.0, 49.1, 48.7, 47.5, 48.9],
    'transport': [12.8, 11.5, 13.2, 18.4, 10.8],
    'queue': [618.5, 8.5, 18.7, 136.3, 8.4],
    'reconfig': [2.2, 3.2, 11.8, 475.5, 3.2],
    'total': [680.5, 72.3, 92.4, 677.7, 71.3]
}


DATA_SENSITIVITY = {
    'loads_x': [0, 1, 2],
    'load_labels': ['LOW', 'MEDIUM', 'HIGH'],
    'dml': [91.8, 680.5, 1072.6],
    'ci_stt': [67.4, 72.3, 80.2],
    'ci_sq': [84.6, 92.4, 104.5],
    'ci_lb': [387.1, 677.7, 1097.6],
    'hybrid_stt': [68.0, 71.3, 81.5]
}


DATA_CROSSPLATFORM = {
    'metrics': ['CI vs DML\nImprovement', 'Best Rule\nPerformance', 'Worst Rule\nPerformance', 'Queue Time\n(% of total)'],
    'simpy': [89.4, 72.3, 677.7, 90.9],
    'plantsim': [33.8, 45.0, 450.0, 85.0]
}


DATA_HEATMAP = {
    'rules': ['STT', 'SQ', 'SPT', 'NA', 'LB'],
    'columns': ['CI\nLOW', 'CI\nMED', 'CI\nHIGH', 'HYB\nLOW', 'HYB\nMED', 'HYB\nHIGH'],
    'values': np.array([
        [26.6, 89.4, 92.5, 25.9, 89.5, 92.4],
        [21.3, 86.4, 90.2, 20.8, 86.1, 89.8],
        [18.7, 86.6, 89.8, 18.2, 86.3, 89.5],
        [12.4, 78.7, 82.3, 11.9, 78.2, 81.9],
        [-321.4, -0.4, -2.3, -315.2, -1.1, -3.0]
    ])
}




GRAY = {
    'dark': '#2d2d2d',
    'medium': '#666666',
    'light': '#999999',
    'lighter': '#cccccc',
    'lightest': '#e6e6e6',
    'white': '#ffffff',
    'black': '#000000'
}

# Global matplotlib settings
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3


def create_figure_4():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    loads = DATA_TOPOLOGY['loads']
    x = np.arange(len(loads))
    width = 0.25
    

    bars1 = ax.bar(x - width, DATA_TOPOLOGY['dml']['mean'], width, 
                   label='DML (Dedicated Line)', 
                   color=GRAY['lightest'],
                   edgecolor=GRAY['dark'], 
                   linewidth=1.5, 
                   yerr=DATA_TOPOLOGY['dml']['std'], 
                   capsize=5,
                   error_kw={'elinewidth': 1.5, 'capthick': 1.5})
    
    bars2 = ax.bar(x, DATA_TOPOLOGY['ci']['mean'], width, 
                   label='CI (Competence Islands)',
                   color=GRAY['medium'],
                   edgecolor=GRAY['dark'], 
                   linewidth=1.5, 
                   yerr=DATA_TOPOLOGY['ci']['std'], 
                   capsize=5,
                   error_kw={'elinewidth': 1.5, 'capthick': 1.5})
    
    bars3 = ax.bar(x + width, DATA_TOPOLOGY['hybrid']['mean'], width, 
                   label='HYBRID (Zoned)',
                   color=GRAY['light'],
                   edgecolor=GRAY['dark'], 
                   linewidth=1.5, 
                   yerr=DATA_TOPOLOGY['hybrid']['std'], 
                   capsize=5,
                   hatch='//',
                   error_kw={'elinewidth': 1.5, 'capthick': 1.5})
    

    for i, imp in enumerate(DATA_TOPOLOGY['improvement']):
        ax.annotate(imp, xy=(x[i], DATA_TOPOLOGY['ci']['mean'][i] + 15), 
                   ha='center', fontsize=11, fontweight='bold', color=GRAY['dark'])
    
    ax.set_ylabel('Throughput Time (min)', fontsize=12)
    ax.set_xlabel('Load Level', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(loads)
    ax.legend(loc='upper left', frameon=True, fontsize=10)
    ax.set_ylim(0, 1200)
    
    ax.set_title('Topology Comparison (STT Routing Rule)', fontsize=14, fontweight='bold', pad=15)
    
    fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'Fig4_Topology_Comparison.png')
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✓ Saved: {filepath}")


def create_figure_5():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    rules = DATA_RULES['rules']
    times = DATA_RULES['throughput_time']['mean']
    

    colors = [GRAY['dark'], GRAY['medium'], GRAY['medium'], GRAY['light'], GRAY['lightest']]
    

    bars = ax.barh(rules, times, color=colors, edgecolor=GRAY['dark'], linewidth=1.5, height=0.6)
    

    ax.axvline(x=DATA_RULES['dml_baseline'], color=GRAY['dark'], linestyle='--', 
               linewidth=2.5, label=f'DML Baseline ({DATA_RULES["dml_baseline"]} min)')
    

    improvements = DATA_RULES['improvement_vs_dml']
    for i, (bar, imp) in enumerate(zip(bars, improvements)):
        ax.text(bar.get_width() + 15, bar.get_y() + bar.get_height()/2, imp, 
                va='center', fontsize=11, fontweight='bold', color=GRAY['dark'])
    
    ax.set_xlabel('Throughput Time (min)', fontsize=12)
    ax.set_ylabel('Routing Rule', fontsize=12)
    ax.set_xlim(0, 800)
    ax.legend(loc='lower right', fontsize=10)
    
    ax.set_title('Routing Rule Performance (CI Topology, MEDIUM Load)', 
                 fontsize=14, fontweight='bold', pad=15)
    
    fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'Fig5_Routing_Rules.png')
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✓ Saved: {filepath}")


def create_figure_6():
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    
    configs = DATA_BREAKDOWN['configs']
    x = np.arange(len(configs))
    width = 0.6
    
    processing = np.array(DATA_BREAKDOWN['processing'])
    transport = np.array(DATA_BREAKDOWN['transport'])
    queue = np.array(DATA_BREAKDOWN['queue'])
    reconfig = np.array(DATA_BREAKDOWN['reconfig'])
    
    # Stacked bars
    p1 = ax.bar(x, processing, width, label='Processing', 
                color=GRAY['dark'], edgecolor=GRAY['black'], linewidth=1)
    p2 = ax.bar(x, transport, width, bottom=processing, label='Transport', 
                color=GRAY['medium'], edgecolor=GRAY['black'], linewidth=1)
    p3 = ax.bar(x, queue, width, bottom=processing+transport, label='Queue',
                color=GRAY['light'], edgecolor=GRAY['black'], linewidth=1)
    p4 = ax.bar(x, reconfig, width, bottom=processing+transport+queue, label='Reconfiguration',
                color=GRAY['lightest'], edgecolor=GRAY['black'], linewidth=1, hatch='//')
    
    # Key value annotations
    ax.annotate('Queue:\n90.9%', xy=(0, 450), fontsize=10, ha='center', 
                fontweight='bold', color=GRAY['black'],
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.annotate('Reconfiguration:\n70.2%', xy=(3, 520), fontsize=10, ha='center', 
                fontweight='bold', color=GRAY['black'],
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_ylabel('Time (min)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=11)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(0, 750)
    
    ax.set_title('Throughput Time Decomposition (MEDIUM Load)', fontsize=14, fontweight='bold', pad=15)
    
    fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'Fig6_Time_Decomposition.png')
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✓ Saved: {filepath}")


def create_figure_7():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    x = DATA_SENSITIVITY['loads_x']
    labels = DATA_SENSITIVITY['load_labels']
    

    ax.plot(x, DATA_SENSITIVITY['dml'], 'o-', linewidth=2.5, markersize=10, 
            label='DML', color=GRAY['black'])
    ax.plot(x, DATA_SENSITIVITY['ci_stt'], 's-', linewidth=2.5, markersize=10, 
            label='CI + STT', color=GRAY['dark'])
    ax.plot(x, DATA_SENSITIVITY['ci_sq'], '^-', linewidth=2.5, markersize=10, 
            label='CI + SQ', color=GRAY['medium'])
    ax.plot(x, DATA_SENSITIVITY['ci_lb'], 'v-', linewidth=2.5, markersize=10, 
            label='CI + LB', color=GRAY['light'])
    ax.plot(x, DATA_SENSITIVITY['hybrid_stt'], 'D-', linewidth=2.5, markersize=10, 
            label='HYBRID + STT', color=GRAY['lighter'], markeredgecolor=GRAY['dark'])
    

    ax.annotate('LB Failure\n(+183%)', xy=(2, 1097.6), xytext=(1.4, 950),
                arrowprops=dict(arrowstyle='->', color=GRAY['dark'], lw=2),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    

    ax.annotate('DML Collapse\n(+1068%)', xy=(2, 1072.6), xytext=(2.3, 850),
                arrowprops=dict(arrowstyle='->', color=GRAY['dark'], lw=2),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    ax.set_ylabel('Throughput Time (min)', fontsize=12)
    ax.set_xlabel('Load Level', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(0, 1200)
    
    ax.set_title('Load Sensitivity Analysis', fontsize=14, fontweight='bold', pad=15)
    
    fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'Fig7_Load_Sensitivity.png')
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✓ Saved: {filepath}")


def create_figure_8():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    metrics = DATA_CROSSPLATFORM['metrics']
    x = np.arange(len(metrics))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, DATA_CROSSPLATFORM['simpy'], width, 
                   label='SimPy (36 workstations)', 
                   color=GRAY['medium'],
                   edgecolor=GRAY['dark'], linewidth=1.5)
    bars2 = ax.bar(x + width/2, DATA_CROSSPLATFORM['plantsim'], width, 
                   label='Plant Simulation (137 workstations)', 
                   color=GRAY['lighter'],
                   edgecolor=GRAY['dark'], linewidth=1.5, hatch='//')
    
    ax.set_ylabel('Value (%, min, or ratio)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.legend(loc='upper right', fontsize=10)
    
    ax.set_title('Cross-Platform Validation Results', fontsize=14, fontweight='bold', pad=15)
    

    ax.text(1.5, -120, 'Consistent conclusions across both platforms', ha='center', 
            fontsize=12, style='italic', color=GRAY['dark'])
    
    fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'Fig8_Cross_Platform.png')
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✓ Saved: {filepath}")


def create_figure_9():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    rules = DATA_HEATMAP['rules']
    columns = DATA_HEATMAP['columns']
    data = DATA_HEATMAP['values']
    
  
    cmap = plt.cm.RdYlGn
    
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=-50, vmax=100)
    
    ax.set_xticks(np.arange(len(columns)))
    ax.set_yticks(np.arange(len(rules)))
    ax.set_xticklabels(columns, fontsize=10)
    ax.set_yticklabels(rules, fontsize=11)
    

    for i in range(len(rules)):
        for j in range(len(columns)):
            val = data[i, j]
         
            color = 'white' if (val > 70 or val < -20) else 'black'
            text = f'{val:+.1f}%' if val > -100 else f'{val:.0f}%'
            ax.text(j, i, text, ha='center', va='center', color=color, 
                   fontsize=10, fontweight='bold')
    
 
    rect = plt.Rectangle((2-0.5, 0-0.5), 1, 1, fill=False, 
                          edgecolor='black', linewidth=3)
    ax.add_patch(rect)
    
  
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Improvement vs DML (%)', fontsize=11)
    
    ax.set_title('Performance Heatmap: Improvement vs DML Baseline', 
                 fontsize=14, fontweight='bold', pad=15)
    
    fig.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, 'Fig9_Heatmap.png')
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"✓ Saved: {filepath}")


def main():
    print("="*60)
    print("Generating figures for the article")
    print("="*60)
    print()
    
    
    create_figure_4()
    create_figure_5()
    create_figure_6()
    create_figure_7()
    create_figure_8()
    create_figure_9()
    


if __name__ == "__main__":
    main()
