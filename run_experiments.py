#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import json
import time
from datetime import datetime
from typing import List, Dict
import numpy as np
from collections import defaultdict

from simulator_extended import (
    TopologyType, RoutingRule, SimulationRunner,
    SimulationMetrics, SystemConfig
)


TOPOLOGIES = [TopologyType.DML, TopologyType.CI, TopologyType.HYBRID]
ROUTING_RULES = [RoutingRule.SPT, RoutingRule.SQ, RoutingRule.STT,
                 RoutingRule.LB, RoutingRule.NA]
LOAD_LEVELS = ['LOW', 'MEDIUM', 'HIGH']
NUM_REPLICATIONS = 5

OUTPUT_DIR = "results_extended"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR


def print_header(experiment_name: str):
    print("\n" + "="*70)
    print(f"   {experiment_name}")
    print("="*70)
    print(f"   Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def save_results_csv(results: List[SimulationMetrics], filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)

    fieldnames = [
        'topology', 'routing_rule', 'load_level', 'replication',
        'failures_enabled', 'variable_reconfig',
        'avg_throughput_time', 'std_throughput_time', 'min_throughput_time', 'max_throughput_time',
        'avg_processing_time', 'avg_transport_time', 'avg_queue_time', 'avg_reconfig_time',
        'avg_failure_wait_time',
        'avg_utilization', 'min_utilization', 'max_utilization',
        'total_failures', 'avg_failure_time_per_ws', 'availability',
        'throughput', 'avg_wip', 'products_completed',
        'avg_alternatives_considered',
        'transport_weight_in_decisions', 'queue_weight_in_decisions',
        'processing_weight_in_decisions', 'reconfig_weight_in_decisions',
        'simulation_time_sec'
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for m in results:
            writer.writerow({
                'topology': m.topology,
                'routing_rule': m.routing_rule,
                'load_level': m.load_level,
                'replication': m.replication,
                'failures_enabled': m.failures_enabled,
                'variable_reconfig': m.variable_reconfig,
                'avg_throughput_time': round(m.avg_throughput_time, 2),
                'std_throughput_time': round(m.std_throughput_time, 2),
                'min_throughput_time': round(m.min_throughput_time, 2),
                'max_throughput_time': round(m.max_throughput_time, 2),
                'avg_processing_time': round(m.avg_processing_time, 2),
                'avg_transport_time': round(m.avg_transport_time, 2),
                'avg_queue_time': round(m.avg_queue_time, 2),
                'avg_reconfig_time': round(m.avg_reconfig_time, 2),
                'avg_failure_wait_time': round(m.avg_failure_wait_time, 2),
                'avg_utilization': round(m.avg_utilization, 2),
                'min_utilization': round(m.min_utilization, 2),
                'max_utilization': round(m.max_utilization, 2),
                'total_failures': m.total_failures,
                'avg_failure_time_per_ws': round(m.avg_failure_time_per_ws, 2),
                'availability': round(m.availability, 2),
                'throughput': round(m.throughput, 3),
                'avg_wip': round(m.avg_wip, 2),
                'products_completed': m.products_completed,
                'avg_alternatives_considered': round(m.avg_alternatives_considered, 2),
                'transport_weight_in_decisions': round(m.transport_weight_in_decisions, 2),
                'queue_weight_in_decisions': round(m.queue_weight_in_decisions, 2),
                'processing_weight_in_decisions': round(m.processing_weight_in_decisions, 2),
                'reconfig_weight_in_decisions': round(m.reconfig_weight_in_decisions, 2),
                'simulation_time_sec': round(m.simulation_time_sec, 3)
            })

    print(f"✓ Results saved: {filepath}")
    return filepath


def save_summary_json(results: List[SimulationMetrics], filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)

    aggregated = defaultdict(list)
    for r in results:
        key = (r.topology, r.routing_rule, r.load_level, r.failures_enabled, r.variable_reconfig)
        aggregated[key].append(r)

    summary = []
    for key, runs in aggregated.items():
        topology, rule, load, failures, var_reconfig = key

        summary.append({
            'topology': topology,
            'routing_rule': rule,
            'load_level': load,
            'failures_enabled': failures,
            'variable_reconfig': var_reconfig,
            'n_replications': len(runs),
            'throughput_time': {
                'mean': round(np.mean([r.avg_throughput_time for r in runs]), 2),
                'std':  round(np.std([r.avg_throughput_time for r in runs]), 2),
                'min':  round(np.min([r.avg_throughput_time for r in runs]), 2),
                'max':  round(np.max([r.avg_throughput_time for r in runs]), 2)
            },
            'components': {
                'processing':   round(np.mean([r.avg_processing_time for r in runs]), 2),
                'transport':    round(np.mean([r.avg_transport_time for r in runs]), 2),
                'queue':        round(np.mean([r.avg_queue_time for r in runs]), 2),
                'reconfig':     round(np.mean([r.avg_reconfig_time for r in runs]), 2),
                'failure_wait': round(np.mean([r.avg_failure_wait_time for r in runs]), 2)
            },
            'utilization':    round(np.mean([r.avg_utilization for r in runs]), 2),
            'availability':   round(np.mean([r.availability for r in runs]), 2),
            'total_failures': round(np.mean([r.total_failures for r in runs]), 1),
            'throughput':     round(np.mean([r.throughput for r in runs]), 3),
            'decision_weights': {
                'transport':  round(np.mean([r.transport_weight_in_decisions for r in runs]), 2),
                'queue':      round(np.mean([r.queue_weight_in_decisions for r in runs]), 2),
                'processing': round(np.mean([r.processing_weight_in_decisions for r in runs]), 2),
                'reconfig':   round(np.mean([r.reconfig_weight_in_decisions for r in runs]), 2)
            }
        })

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✓ Summary saved: {filepath}")
    return filepath


def print_progress(current: int, total: int, desc: str, result: SimulationMetrics = None):
    pct = current / total * 100
    if result:
        print(f"  [{current:3d}/{total}] {pct:5.1f}% | {desc} | TT={result.avg_throughput_time:.1f} min")
    else:
        print(f"  [{current:3d}/{total}] {pct:5.1f}% | {desc}")


def run_experiment_1_baseline():
    print_header("EXPERIMENT 1: BASELINE (no failures, fixed reconfig)")

    runner = SimulationRunner()
    results = []

    total_dml   = len(LOAD_LEVELS) * NUM_REPLICATIONS
    total_other = 2 * len(ROUTING_RULES) * len(LOAD_LEVELS) * NUM_REPLICATIONS
    total   = total_dml + total_other
    current = 0

    print(f"Total simulations: {total}")
    print("-" * 50)

    print("\n▶ DML experiments...")
    for load in LOAD_LEVELS:
        for rep in range(NUM_REPLICATIONS):
            current += 1
            result = runner.run_single(
                topology=TopologyType.DML,
                routing_rule=RoutingRule.STT,
                load_level=load,
                replication=rep,
                failures_enabled=False,
                variable_reconfig=False
            )
            results.append(result)
            print_progress(current, total, f"DML | {load} | Rep {rep+1}", result)

    print("\n▶ CI experiments...")
    for rule in ROUTING_RULES:
        for load in LOAD_LEVELS:
            for rep in range(NUM_REPLICATIONS):
                current += 1
                result = runner.run_single(
                    topology=TopologyType.CI,
                    routing_rule=rule,
                    load_level=load,
                    replication=rep,
                    failures_enabled=False,
                    variable_reconfig=False
                )
                results.append(result)
                print_progress(current, total, f"CI | {rule.name} | {load} | Rep {rep+1}", result)

    print("\n▶ HYBRID experiments...")
    for rule in ROUTING_RULES:
        for load in LOAD_LEVELS:
            for rep in range(NUM_REPLICATIONS):
                current += 1
                result = runner.run_single(
                    topology=TopologyType.HYBRID,
                    routing_rule=rule,
                    load_level=load,
                    replication=rep,
                    failures_enabled=False,
                    variable_reconfig=False
                )
                results.append(result)
                print_progress(current, total, f"HYBRID | {rule.name} | {load} | Rep {rep+1}", result)

    save_results_csv(results, "exp1_baseline.csv")
    save_summary_json(results, "exp1_baseline_summary.json")

    return results


def run_experiment_2_with_failures():
    print_header("EXPERIMENT 2: WITH MACHINE FAILURES (R1.3)")

    runner = SimulationRunner()
    results = []

    test_rules      = [RoutingRule.STT, RoutingRule.SPT, RoutingRule.SQ, RoutingRule.LB]
    test_topologies = [TopologyType.CI, TopologyType.HYBRID]

    total   = len(test_topologies) * len(test_rules) * len(LOAD_LEVELS) * NUM_REPLICATIONS
    current = 0

    print(f"Total simulations: {total}")
    print(f"MTBF: 480 min, MTTR: 15 min")
    print("-" * 50)

    for topo in test_topologies:
        print(f"\n▶ {topo.name} experiments...")
        for rule in test_rules:
            for load in LOAD_LEVELS:
                for rep in range(NUM_REPLICATIONS):
                    current += 1
                    result = runner.run_single(
                        topology=topo,
                        routing_rule=rule,
                        load_level=load,
                        replication=rep,
                        failures_enabled=True,
                        variable_reconfig=False
                    )
                    results.append(result)
                    print_progress(current, total,
                                   f"{topo.name} | {rule.name} | {load} | Rep {rep+1} | Failures: {result.total_failures}",
                                   result)

    save_results_csv(results, "exp2_with_failures.csv")
    save_summary_json(results, "exp2_with_failures_summary.json")

    return results


def run_experiment_3_variable_reconfig():
    print_header("EXPERIMENT 3: VARIABLE RECONFIGURATION TIME (R1.5)")

    runner = SimulationRunner()
    results = []

    test_rules      = [RoutingRule.STT, RoutingRule.SPT, RoutingRule.SQ, RoutingRule.LB]
    test_topologies = [TopologyType.CI, TopologyType.HYBRID]

    total   = len(test_topologies) * len(test_rules) * len(LOAD_LEVELS) * NUM_REPLICATIONS
    current = 0

    print(f"Total simulations: {total}")
    print(f"Reconfig times: same_op=0, same_group=2, adjacent=3.5, distant=5 min")
    print("-" * 50)

    for topo in test_topologies:
        print(f"\n▶ {topo.name} experiments...")
        for rule in test_rules:
            for load in LOAD_LEVELS:
                for rep in range(NUM_REPLICATIONS):
                    current += 1
                    result = runner.run_single(
                        topology=topo,
                        routing_rule=rule,
                        load_level=load,
                        replication=rep,
                        failures_enabled=False,
                        variable_reconfig=True
                    )
                    results.append(result)
                    print_progress(current, total,
                                   f"{topo.name} | {rule.name} | {load} | Rep {rep+1} | Reconfig: {result.avg_reconfig_time:.1f}",
                                   result)

    save_results_csv(results, "exp3_variable_reconfig.csv")
    save_summary_json(results, "exp3_variable_reconfig_summary.json")

    return results


def run_experiment_4_combined():
    print_header("EXPERIMENT 4: COMBINED SCENARIO (failures + var. reconfig)")

    runner = SimulationRunner()
    results = []

    test_rules      = [RoutingRule.STT, RoutingRule.SPT, RoutingRule.SQ, RoutingRule.LB]
    test_topologies = [TopologyType.CI, TopologyType.HYBRID]

    total   = len(test_topologies) * len(test_rules) * len(LOAD_LEVELS) * NUM_REPLICATIONS
    current = 0

    print(f"Total simulations: {total}")
    print("-" * 50)

    for topo in test_topologies:
        print(f"\n▶ {topo.name} experiments...")
        for rule in test_rules:
            for load in LOAD_LEVELS:
                for rep in range(NUM_REPLICATIONS):
                    current += 1
                    result = runner.run_single(
                        topology=topo,
                        routing_rule=rule,
                        load_level=load,
                        replication=rep,
                        failures_enabled=True,
                        variable_reconfig=True
                    )
                    results.append(result)
                    print_progress(current, total,
                                   f"{topo.name} | {rule.name} | {load} | Rep {rep+1}",
                                   result)

    save_results_csv(results, "exp4_combined.csv")
    save_summary_json(results, "exp4_combined_summary.json")

    return results


def run_experiment_5_stt_analysis():
    print_header("EXPERIMENT 5: STT SUPERIORITY ANALYSIS (R1.5)")

    runner = SimulationRunner()
    results = []

    test_rules = [RoutingRule.STT, RoutingRule.SPT, RoutingRule.SQ]

    n_reps  = 10
    total   = len(test_rules) * len(LOAD_LEVELS) * n_reps
    current = 0

    print(f"Total simulations: {total}")
    print("Detailed tracking of decision components")
    print("-" * 50)

    for rule in test_rules:
        print(f"\n▶ {rule.name} experiments...")
        for load in LOAD_LEVELS:
            for rep in range(n_reps):
                current += 1
                result = runner.run_single(
                    topology=TopologyType.CI,
                    routing_rule=rule,
                    load_level=load,
                    replication=rep,
                    failures_enabled=False,
                    variable_reconfig=True
                )
                results.append(result)

                if rule == RoutingRule.STT:
                    print_progress(current, total,
                                   f"{rule.name} | {load} | Rep {rep+1} | "
                                   f"T:{result.transport_weight_in_decisions:.0f}% "
                                   f"Q:{result.queue_weight_in_decisions:.0f}% "
                                   f"P:{result.processing_weight_in_decisions:.0f}% "
                                   f"R:{result.reconfig_weight_in_decisions:.0f}%",
                                   result)
                else:
                    print_progress(current, total, f"{rule.name} | {load} | Rep {rep+1}", result)

    save_results_csv(results, "exp5_stt_analysis.csv")
    save_summary_json(results, "exp5_stt_analysis_summary.json")

    return results


def generate_summary_report(all_results: Dict[str, List[SimulationMetrics]]):
    filepath = os.path.join(OUTPUT_DIR, "SUMMARY_REPORT.txt")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SÚHRNNÁ SPRÁVA Z ROZŠÍRENÝCH EXPERIMENTOV\n")
        f.write(f"Vygenerované: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")

        for exp_name, results in all_results.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"{exp_name.upper()}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Počet simulácií: {len(results)}\n\n")

            aggregated = defaultdict(list)
            for r in results:
                key = (r.topology, r.routing_rule, r.load_level)
                aggregated[key].append(r)

            f.write(f"{'Topológia':<10} {'Pravidlo':<8} {'Záťaž':<8} {'TT (min)':<15} {'Util %':<10} {'Avail %':<10}\n")
            f.write("-"*70 + "\n")

            for key in sorted(aggregated.keys()):
                topo, rule, load = key
                runs = aggregated[key]

                tt_mean = np.mean([r.avg_throughput_time for r in runs])
                tt_std  = np.std([r.avg_throughput_time for r in runs])
                util    = np.mean([r.avg_utilization for r in runs])
                avail   = np.mean([r.availability for r in runs])

                f.write(f"{topo:<10} {rule:<8} {load:<8} {tt_mean:>6.1f}±{tt_std:<5.1f}  {util:>6.1f}     {avail:>6.1f}\n")

            f.write("\n")

    print(f"\n✓ Summary report: {filepath}")


def main():
    print("\n" + "="*70)
    print("   EXTENDED EXPERIMENTS FOR REVIEWER RESPONSE")
    print("   Competence Islands Manufacturing System")
    print("="*70)
    print(f"   Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    ensure_output_dir()

    all_results = {}
    total_start = time.time()

    print("\n" + "="*70)
    print("EXPERIMENT PLAN:")
    print("-"*70)
    print("1. Baseline (no failures, fixed reconfig)")
    print("2. With machine failures (MTBF=480, MTTR=15)")
    print("3. Variable reconfiguration time")
    print("4. Combined scenario (failures + var. reconfig)")
    print("5. STT superiority analysis")
    print("-"*70)

    input("\nPress ENTER to start experiments...")

    exp1_results = run_experiment_1_baseline()
    all_results['Experiment 1: Baseline'] = exp1_results

    exp2_results = run_experiment_2_with_failures()
    all_results['Experiment 2: S poruchami'] = exp2_results

    exp3_results = run_experiment_3_variable_reconfig()
    all_results['Experiment 3: Variabilný reconfig'] = exp3_results

    exp4_results = run_experiment_4_combined()
    all_results['Experiment 4: Kombinovaný'] = exp4_results

    exp5_results = run_experiment_5_stt_analysis()
    all_results['Experiment 5: STT analýza'] = exp5_results

    generate_summary_report(all_results)

    total_time = time.time() - total_start
    total_sims = sum(len(r) for r in all_results.values())

    print("\n" + "="*70)
    print("   COMPLETED")
    print("="*70)
    print(f"  Total time:        {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"  Total simulations: {total_sims}")
    print(f"  Average time/sim:  {total_time/total_sims:.2f} seconds")
    print(f"  Output directory:  {OUTPUT_DIR}/")
    print("="*70)
    print("\nFiles for analysis:")
    for f in os.listdir(OUTPUT_DIR):
        print(f"  - {f}")
    print("="*70 + "\n")


def run_quick_test():
    global NUM_REPLICATIONS
    NUM_REPLICATIONS = 1

    print("\n⚡ QUICK TEST (1 replication)")
    ensure_output_dir()

    runner = SimulationRunner()

    tests = [
        ("Baseline",      False, False),
        ("With failures", True,  False),
        ("Var. reconfig", False, True),
        ("Combined",      True,  True),
    ]

    for name, failures, var_reconfig in tests:
        print(f"\n▶ Test: {name}")
        result = runner.run_single(
            topology=TopologyType.CI,
            routing_rule=RoutingRule.STT,
            load_level='MEDIUM',
            replication=0,
            failures_enabled=failures,
            variable_reconfig=var_reconfig,
            verbose=True
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        main()
