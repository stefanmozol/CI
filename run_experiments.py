#!/usr/bin/env python3


import os
import sys
import csv
import time
from datetime import datetime
from typing import List
import itertools


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulator import (
    TopologyType, RoutingRule, SimulationRunner, 
    SimulationMetrics, SystemConfig
)


def print_header():
    """Vypíše hlavičku"""
    print("\n" + "="*70)
    print("   COMPETENCE ISLAND MANUFACTURING SIMULATION")
    print("   Porovnanie výrobných systémov: DML vs CI vs Hybrid")
    print("="*70)
    print(f"   Čas spustenia: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def print_experiment_plan(topologies, rules, loads, replications):
    """Vypíše plán experimentov"""
    total = len(topologies) * len(rules) * len(loads) * replications
    
    print("PLÁN EXPERIMENTOV:")
    print("-"*50)
    print(f"  Topológie:          {[t.name for t in topologies]}")
    print(f"  Routing pravidlá:   {[r.name for r in rules]}")
    print(f"  Úrovne zaťaženia:   {loads}")
    print(f"  Replikácie:         {replications}")
    print("-"*50)
    print(f"  CELKOM:             {total} simulácií")
    print("-"*50 + "\n")
    
    return total


def save_results(results: List[SimulationMetrics], filename: str):
    """Uloží výsledky do CSV"""
    

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    

    fieldnames = [
        'topology', 'routing_rule', 'load_level', 'replication',
        'avg_throughput_time', 'std_throughput_time', 'min_throughput_time', 'max_throughput_time',
        'avg_processing_time', 'avg_transport_time', 'avg_queue_time', 'avg_reconfig_time',
        'avg_utilization', 'min_utilization', 'max_utilization',
        'throughput', 'avg_wip', 'products_completed', 'simulation_time_sec'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for m in results:
            writer.writerow({
                'topology': m.topology,
                'routing_rule': m.routing_rule,
                'load_level': m.load_level,
                'replication': m.replication,
                'avg_throughput_time': round(m.avg_throughput_time, 2),
                'std_throughput_time': round(m.std_throughput_time, 2),
                'min_throughput_time': round(m.min_throughput_time, 2),
                'max_throughput_time': round(m.max_throughput_time, 2),
                'avg_processing_time': round(m.avg_processing_time, 2),
                'avg_transport_time': round(m.avg_transport_time, 2),
                'avg_queue_time': round(m.avg_queue_time, 2),
                'avg_reconfig_time': round(m.avg_reconfig_time, 2),
                'avg_utilization': round(m.avg_utilization, 2),
                'min_utilization': round(m.min_utilization, 2),
                'max_utilization': round(m.max_utilization, 2),
                'throughput': round(m.throughput, 3),
                'avg_wip': round(m.avg_wip, 2),
                'products_completed': m.products_completed,
                'simulation_time_sec': round(m.simulation_time_sec, 3)
            })
    
    print(f"\n✓ Výsledky uložené do: {filename}")


def print_summary_table(results: List[SimulationMetrics]):
    """Vypíše súhrnnú tabuľku výsledkov"""
    
    print("\n" + "="*90)
    print("   SÚHRNNÉ VÝSLEDKY (priemer cez replikácie)")
    print("="*90)
    

    from collections import defaultdict
    import numpy as np
    
    aggregated = defaultdict(list)
    
    for r in results:
        key = (r.topology, r.routing_rule, r.load_level)
        aggregated[key].append(r)
    

    print(f"\n{'Topológia':<10} {'Pravidlo':<8} {'Záťaž':<8} {'Throughput':<15} {'Utiliz.':<10} {'WIP':<8} {'Prod/h':<8}")
    print("-"*90)
    

    dml_baselines = {}
    

    for key, runs in aggregated.items():
        if key[0] == 'DML':
            load = key[2]
            avg_tt = np.mean([r.avg_throughput_time for r in runs])
            dml_baselines[load] = avg_tt
    

    for key in sorted(aggregated.keys()):
        topology, rule, load = key
        runs = aggregated[key]
        
        avg_tt = np.mean([r.avg_throughput_time for r in runs])
        std_tt = np.std([r.avg_throughput_time for r in runs])
        avg_util = np.mean([r.avg_utilization for r in runs])
        avg_wip = np.mean([r.avg_wip for r in runs])
        avg_throughput = np.mean([r.throughput for r in runs])
        

        improvement = ""
        if topology != 'DML' and load in dml_baselines:
            baseline = dml_baselines[load]
            pct = (baseline - avg_tt) / baseline * 100
            improvement = f" ({pct:+.1f}%)"
        
        print(f"{topology:<10} {rule:<8} {load:<8} {avg_tt:>6.1f}±{std_tt:<5.1f} min{improvement:<8} {avg_util:>6.1f}%    {avg_wip:>5.1f}    {avg_throughput:>5.2f}")
    
    print("-"*90)


def print_best_results(results: List[SimulationMetrics]):
    """Vypíše najlepšie výsledky"""
    
    import numpy as np
    from collections import defaultdict
    
    print("\n" + "="*70)
    print("   NAJLEPŠIE KONFIGURÁCIE (podľa throughput time)")
    print("="*70)
    

    aggregated = defaultdict(list)
    for r in results:
        key = (r.topology, r.routing_rule, r.load_level)
        aggregated[key].append(r)
    

    for load in ['LOW', 'MEDIUM', 'HIGH']:
        print(f"\n  {load} LOAD:")
        
        best = None
        best_time = float('inf')
        
        for key, runs in aggregated.items():
            if key[2] != load:
                continue
            avg_tt = np.mean([r.avg_throughput_time for r in runs])
            if avg_tt < best_time:
                best_time = avg_tt
                best = key
        
        if best:
            runs = aggregated[best]
            avg_tt = np.mean([r.avg_throughput_time for r in runs])
            avg_util = np.mean([r.avg_utilization for r in runs])
            print(f"    → {best[0]} + {best[1]}: {avg_tt:.1f} min (util: {avg_util:.1f}%)")


def main():

    
    print_header()
    

    topologies = [TopologyType.DML, TopologyType.CI, TopologyType.HYBRID]
    

    routing_rules = [RoutingRule.SPT, RoutingRule.SQ, RoutingRule.STT, 
                     RoutingRule.LB, RoutingRule.NA]
    
    load_levels = ['LOW', 'MEDIUM', 'HIGH']
    num_replications = 5
    

    dml_rules = [RoutingRule.STT]  # Dummy - DML má fixný routing
    

    total_dml = len(dml_rules) * len(load_levels) * num_replications
    total_other = (len(topologies) - 1) * len(routing_rules) * len(load_levels) * num_replications
    total = total_dml + total_other
    
    print("PLÁN EXPERIMENTOV:")
    print("-"*50)
    print(f"  DML experimenty:    {total_dml}")
    print(f"  CI+Hybrid exp.:     {total_other}")
    print(f"  CELKOM:             {total} simulácií")
    print("-"*50 + "\n")
    

    runner = SimulationRunner()
    all_results = []
    
    current = 0
    start_total = time.time()
    

    print("▶ Spúšťam DML experimenty...")
    for load in load_levels:
        for rep in range(num_replications):
            current += 1
            print(f"  [{current}/{total}] DML | {load} | Rep {rep+1}...", end=" ", flush=True)
            
            result = runner.run_single(
                topology=TopologyType.DML,
                routing_rule=RoutingRule.STT,
                load_level=load,
                replication=rep,
                verbose=False
            )
            all_results.append(result)
            print(f"✓ {result.avg_throughput_time:.1f} min")
    

    print("\n▶ Spúšťam CI experimenty...")
    for rule in routing_rules:
        for load in load_levels:
            for rep in range(num_replications):
                current += 1
                print(f"  [{current}/{total}] CI | {rule.name} | {load} | Rep {rep+1}...", end=" ", flush=True)
                
                result = runner.run_single(
                    topology=TopologyType.CI,
                    routing_rule=rule,
                    load_level=load,
                    replication=rep,
                    verbose=False
                )
                all_results.append(result)
                print(f"✓ {result.avg_throughput_time:.1f} min")
    

    print("\n▶ Spúšťam HYBRID experimenty...")
    for rule in routing_rules:
        for load in load_levels:
            for rep in range(num_replications):
                current += 1
                print(f"  [{current}/{total}] HYBRID | {rule.name} | {load} | Rep {rep+1}...", end=" ", flush=True)
                
                result = runner.run_single(
                    topology=TopologyType.HYBRID,
                    routing_rule=rule,
                    load_level=load,
                    replication=rep,
                    verbose=False
                )
                all_results.append(result)
                print(f"✓ {result.avg_throughput_time:.1f} min")
    
    total_time = time.time() - start_total
    

    results_file = "results/experiment_results.csv"
    save_results(all_results, results_file)
    

    print_summary_table(all_results)
    print_best_results(all_results)
    

    print("\n" + "="*70)
    print("   DOKONČENÉ")
    print("="*70)
    print(f"  Celkový čas:       {total_time:.1f} sekúnd ({total_time/60:.1f} minút)")
    print(f"  Priemerný čas/sim: {total_time/total:.2f} sekúnd")
    print(f"  Výsledky uložené:  {results_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
