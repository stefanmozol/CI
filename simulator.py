#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import simpy
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import time
import json


class TopologyType(Enum):
    DML = "Dedicated Manufacturing Line"
    CI = "Competence Islands"
    HYBRID = "Hybrid Zoned CI"


class RoutingRule(Enum):
    SPT = "Shortest Processing Time"
    SQ = "Shortest Queue"
    STT = "Shortest Total Time"
    LB = "Load Balancing"
    NA = "Nearest Available"


@dataclass
class Operation:
    op_id: int
    op_type: str


@dataclass
class Product:
    product_id: int
    name: str
    operations: List[Operation]
    current_op_index: int = 0
    entry_time: float = 0.0
    exit_time: float = 0.0
    total_transport_time: float = 0.0
    total_queue_time: float = 0.0
    total_processing_time: float = 0.0
    total_reconfig_time: float = 0.0
    total_failure_wait_time: float = 0.0
    visited_workstations: List[str] = field(default_factory=list)
    routing_decisions: List[Dict] = field(default_factory=list)


@dataclass
class Workstation:
    ws_id: int
    name: str
    ws_type: str
    competencies: List[str]
    position: Tuple[int, int]
    zone: int = 0
    queue_length: int = 0
    is_processing: bool = False
    is_failed: bool = False
    current_setting: Optional[str] = None
    total_busy_time: float = 0.0
    total_idle_time: float = 0.0
    total_failure_time: float = 0.0
    products_processed: int = 0
    failure_count: int = 0
    resource: Optional[simpy.Resource] = None
    failure_process: Optional[object] = None


@dataclass
class RoutingDecision:
    product_id: int
    operation: str
    timestamp: float
    selected_ws: str
    rule_used: str
    transport_time: float
    estimated_queue_time: float
    processing_time: float
    reconfig_time: float
    total_score: float
    alternatives_count: int
    alternatives_scores: List[Dict] = field(default_factory=list)


@dataclass
class SimulationMetrics:
    topology: str
    routing_rule: str
    load_level: str
    replication: int
    failures_enabled: bool = False
    variable_reconfig: bool = False
    avg_throughput_time: float = 0.0
    std_throughput_time: float = 0.0
    min_throughput_time: float = 0.0
    max_throughput_time: float = 0.0
    avg_processing_time: float = 0.0
    avg_transport_time: float = 0.0
    avg_queue_time: float = 0.0
    avg_reconfig_time: float = 0.0
    avg_failure_wait_time: float = 0.0
    avg_utilization: float = 0.0
    min_utilization: float = 0.0
    max_utilization: float = 0.0
    total_failures: int = 0
    avg_failure_time_per_ws: float = 0.0
    availability: float = 100.0
    throughput: float = 0.0
    avg_wip: float = 0.0
    products_completed: int = 0
    avg_alternatives_considered: float = 0.0
    transport_weight_in_decisions: float = 0.0
    queue_weight_in_decisions: float = 0.0
    processing_weight_in_decisions: float = 0.0
    reconfig_weight_in_decisions: float = 0.0
    simulation_time_sec: float = 0.0


class SystemConfig:

    GRID_SIZE = 6

    WORKSTATION_TYPES = {
        'A': {'competencies': ['OP1', 'OP2'], 'positions': [(0,0), (0,1), (1,0), (1,1)]},
        'B': {'competencies': ['OP2', 'OP3'], 'positions': [(0,2), (0,3), (1,2), (1,3)]},
        'C': {'competencies': ['OP3', 'OP4'], 'positions': [(0,4), (0,5), (1,4), (1,5)]},
        'D': {'competencies': ['OP4', 'OP5'], 'positions': [(2,0), (2,1), (3,0), (3,1)]},
        'E': {'competencies': ['OP5', 'OP6', 'OP7'], 'positions': [(2,2), (2,3), (3,2), (3,3)]},
        'F': {'competencies': ['OP6', 'OP7'], 'positions': [(2,4), (2,5), (3,4), (3,5)]},
        'G': {'competencies': ['OP7', 'OP8'], 'positions': [(4,0), (4,1), (5,0), (5,1)]},
        'H': {'competencies': ['OP8', 'OP9'], 'positions': [(4,2), (4,3), (5,2), (5,3)]},
        'I': {'competencies': ['OP9', 'OP10'], 'positions': [(4,4), (4,5), (5,4), (5,5)]},
    }

    PROCESSING_TIMES = {
        ('A', 'OP1'): (8.0, 1.5),  ('A', 'OP2'): (10.0, 2.0),
        ('B', 'OP2'): (9.0, 1.8),  ('B', 'OP3'): (11.0, 2.2),
        ('C', 'OP3'): (10.0, 2.0), ('C', 'OP4'): (12.0, 2.5),
        ('D', 'OP4'): (11.0, 2.2), ('D', 'OP5'): (13.0, 2.8),
        ('E', 'OP5'): (12.0, 2.5), ('E', 'OP6'): (14.0, 3.0), ('E', 'OP7'): (15.0, 3.2),
        ('F', 'OP6'): (13.0, 2.8), ('F', 'OP7'): (14.0, 3.0),
        ('G', 'OP7'): (13.5, 2.9), ('G', 'OP8'): (12.0, 2.5),
        ('H', 'OP8'): (11.0, 2.2), ('H', 'OP9'): (10.0, 2.0),
        ('I', 'OP9'): (9.0, 1.8),  ('I', 'OP10'): (8.0, 1.5),
    }

    TRANSPORT_TIME_PER_UNIT = 1.0

    OPERATION_GROUPS = {
        'OP1': 'PREP', 'OP2': 'PREP', 'OP3': 'PREP',
        'OP4': 'ASSEMBLY', 'OP5': 'ASSEMBLY', 'OP6': 'ASSEMBLY', 'OP7': 'ASSEMBLY',
        'OP8': 'FINISH', 'OP9': 'FINISH', 'OP10': 'FINISH'
    }

    RECONFIG_TIMES = {
        'same_op':       0.0,
        'same_group':    2.0,
        'adjacent_group': 3.5,
        'distant_group': 5.0,
    }

    RECONFIG_TIME_DEFAULT = 3.0

    FAILURES_ENABLED = False

    MTBF = 480.0
    MTTR_MEAN = 15.0
    MTTR_STD = 5.0

    FAILURE_RATES_BY_TYPE = {
        'A': 1.0, 'B': 1.0, 'C': 1.0,
        'D': 1.2, 'E': 1.3, 'F': 1.2,
        'G': 1.0, 'H': 1.0, 'I': 1.0,
    }

    SIMULATION_LENGTH = 3000
    WARMUP_PERIOD = 300
    NUM_PRODUCTS = 500

    LOAD_LEVELS = {
        'LOW':    8.0,
        'MEDIUM': 5.0,
        'HIGH':   3.0
    }

    DML_ASSIGNMENT = {
        'OP1': 'A', 'OP2': 'B', 'OP3': 'C', 'OP4': 'D', 'OP5': 'E',
        'OP6': 'F', 'OP7': 'G', 'OP8': 'H', 'OP9': 'I', 'OP10': 'I'
    }

    HYBRID_ZONES = {
        0: ['A', 'B', 'C'],
        1: ['D', 'E', 'F'],
        2: ['G', 'H', 'I']
    }


class ProductGenerator:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.all_operations = ['OP1', 'OP2', 'OP3', 'OP4', 'OP5',
                               'OP6', 'OP7', 'OP8', 'OP9', 'OP10']

    def generate_products(self, num_products: int) -> List[Product]:
        products = []

        for i in range(num_products):
            num_ops = self.rng.randint(5, 8)
            available = self.all_operations.copy()
            selected = []

            while len(selected) < num_ops and available:
                candidates = available[:min(4, len(available))]
                op = self.rng.choice(candidates)
                selected.append(op)
                idx = available.index(op)
                available = available[idx + 1:]

            operations = [Operation(op_id=j, op_type=op) for j, op in enumerate(selected)]

            product = Product(
                product_id=i,
                name=f"Product_{i:03d}",
                operations=operations
            )
            products.append(product)

        return products


class ManufacturingSystem:

    def __init__(self, env: simpy.Environment, topology: TopologyType,
                 routing_rule: RoutingRule, config: SystemConfig, seed: int = 42,
                 failures_enabled: bool = False, variable_reconfig: bool = True):

        self.env = env
        self.topology = topology
        self.routing_rule = routing_rule
        self.config = config
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        self.failures_enabled = failures_enabled
        self.variable_reconfig = variable_reconfig

        self.workstations: Dict[str, Workstation] = {}
        self._create_workstations()

        self.completed_products: List[Product] = []
        self.wip_history: List[Tuple[float, int]] = []
        self.current_wip = 0

        self.all_routing_decisions: List[RoutingDecision] = []

        self.entry_position = (-1, 2)

        if self.failures_enabled:
            self._start_failure_processes()

    def _create_workstations(self):
        ws_id = 0
        for ws_type, config in self.config.WORKSTATION_TYPES.items():
            for pos in config['positions']:
                zone = 0
                for z, types in self.config.HYBRID_ZONES.items():
                    if ws_type in types:
                        zone = z
                        break

                capacity = 2 if self.topology == TopologyType.DML else 1

                ws = Workstation(
                    ws_id=ws_id,
                    name=f"{ws_type}_{ws_id}",
                    ws_type=ws_type,
                    competencies=config['competencies'].copy(),
                    position=pos,
                    zone=zone,
                    resource=simpy.Resource(self.env, capacity=capacity)
                )
                self.workstations[ws.name] = ws
                ws_id += 1

    def _start_failure_processes(self):
        for ws in self.workstations.values():
            self.env.process(self._failure_process(ws))

    def _failure_process(self, ws: Workstation):
        while True:
            failure_rate = self.config.FAILURE_RATES_BY_TYPE.get(ws.ws_type, 1.0)
            ttf = self.rng.expovariate(failure_rate / self.config.MTBF)
            yield self.env.timeout(ttf)

            ws.is_failed = True
            ws.failure_count += 1
            failure_start = self.env.now

            repair_time = self.np_rng.lognormal(
                np.log(self.config.MTTR_MEAN),
                self.config.MTTR_STD / self.config.MTTR_MEAN
            )
            repair_time = max(5.0, repair_time)

            yield self.env.timeout(repair_time)

            ws.is_failed = False
            ws.total_failure_time += self.env.now - failure_start

    def get_reconfig_time(self, ws: Workstation, new_op: str) -> float:
        if not self.variable_reconfig:
            if ws.current_setting == new_op:
                return 0.0
            return self.config.RECONFIG_TIME_DEFAULT

        if ws.current_setting == new_op:
            return 0.0

        if ws.current_setting is None:
            return self.config.RECONFIG_TIMES['same_group']

        old_group = self.config.OPERATION_GROUPS.get(ws.current_setting, 'UNKNOWN')
        new_group = self.config.OPERATION_GROUPS.get(new_op, 'UNKNOWN')

        if old_group == new_group:
            return self.config.RECONFIG_TIMES['same_group']

        group_order = ['PREP', 'ASSEMBLY', 'FINISH']
        try:
            old_idx = group_order.index(old_group)
            new_idx = group_order.index(new_group)
            if abs(old_idx - new_idx) == 1:
                return self.config.RECONFIG_TIMES['adjacent_group']
            else:
                return self.config.RECONFIG_TIMES['distant_group']
        except ValueError:
            return self.config.RECONFIG_TIME_DEFAULT

    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_transport_time(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        distance = self.manhattan_distance(from_pos, to_pos)
        return distance * self.config.TRANSPORT_TIME_PER_UNIT

    def get_processing_time(self, ws: Workstation, op_type: str) -> float:
        key = (ws.ws_type, op_type)
        if key in self.config.PROCESSING_TIMES:
            mean, std = self.config.PROCESSING_TIMES[key]
            proc_time = self.np_rng.lognormal(np.log(mean), std / mean)
            return max(1.0, proc_time)
        return 10.0

    def get_capable_workstations(self, op_type: str, current_zone: int = -1) -> List[Workstation]:
        capable = []

        for ws in self.workstations.values():
            if op_type not in ws.competencies:
                continue

            if self.failures_enabled and ws.is_failed:
                continue

            if self.topology == TopologyType.DML:
                if ws.ws_type != self.config.DML_ASSIGNMENT.get(op_type):
                    continue

            elif self.topology == TopologyType.HYBRID:
                if current_zone >= 0 and ws.zone < current_zone:
                    continue

            capable.append(ws)

        return capable

    def select_workstation(self, product: Product, current_pos: Tuple[int, int],
                           current_zone: int) -> Optional[Workstation]:

        if product.current_op_index >= len(product.operations):
            return None

        op = product.operations[product.current_op_index]
        capable = self.get_capable_workstations(op.op_type, current_zone)

        if not capable:
            return None

        if self.topology == TopologyType.DML:
            selected = capable[0]
            self._record_decision(product, op, current_pos, selected, capable, {})
            return selected

        scores = []
        for ws in capable:
            transport = self.get_transport_time(current_pos, ws.position)
            queue_estimate = ws.queue_length * 10.0
            proc = self.get_processing_time(ws, op.op_type)
            reconfig = self.get_reconfig_time(ws, op.op_type)

            scores.append({
                'ws': ws,
                'transport': transport,
                'queue': queue_estimate,
                'processing': proc,
                'reconfig': reconfig,
                'total': transport + queue_estimate + proc + reconfig
            })

        if self.routing_rule == RoutingRule.SPT:
            selected_score = min(scores, key=lambda x: x['processing'])

        elif self.routing_rule == RoutingRule.SQ:
            selected_score = min(scores, key=lambda x: x['ws'].queue_length)

        elif self.routing_rule == RoutingRule.STT:
            selected_score = min(scores, key=lambda x: x['total'])

        elif self.routing_rule == RoutingRule.LB:
            def utilization(s):
                ws = s['ws']
                total = ws.total_busy_time + ws.total_idle_time
                return ws.total_busy_time / total if total > 0 else 0
            selected_score = min(scores, key=utilization)

        elif self.routing_rule == RoutingRule.NA:
            available = [s for s in scores if s['ws'].queue_length < 3]
            if not available:
                available = scores
            selected_score = min(available, key=lambda x: x['transport'])

        else:
            selected_score = scores[0]

        selected = selected_score['ws']
        self._record_decision(product, op, current_pos, selected, capable, selected_score)

        return selected

    def _record_decision(self, product: Product, op: Operation, current_pos: Tuple[int, int],
                         selected: Workstation, capable: List[Workstation], score: Dict):

        decision = RoutingDecision(
            product_id=product.product_id,
            operation=op.op_type,
            timestamp=self.env.now,
            selected_ws=selected.name,
            rule_used=self.routing_rule.name,
            transport_time=score.get('transport', 0),
            estimated_queue_time=score.get('queue', 0),
            processing_time=score.get('processing', 0),
            reconfig_time=score.get('reconfig', 0),
            total_score=score.get('total', 0),
            alternatives_count=len(capable)
        )

        self.all_routing_decisions.append(decision)

        product.routing_decisions.append({
            'op': op.op_type,
            'ws': selected.name,
            'time': self.env.now,
            'components': score
        })

    def process_product(self, product: Product):
        product.entry_time = self.env.now
        current_pos = self.entry_position
        current_zone = -1

        self.current_wip += 1
        self.wip_history.append((self.env.now, self.current_wip))

        while product.current_op_index < len(product.operations):
            op = product.operations[product.current_op_index]

            ws = self.select_workstation(product, current_pos, current_zone)
            if ws is None:
                if self.failures_enabled:
                    yield self.env.timeout(1.0)
                    continue
                print(f"ERROR: No workstation found for {op.op_type}")
                break

            transport_time = self.get_transport_time(current_pos, ws.position)
            if transport_time > 0:
                yield self.env.timeout(transport_time)
                product.total_transport_time += transport_time

            ws.queue_length += 1
            queue_start = self.env.now

            with ws.resource.request() as req:
                yield req
                queue_time = self.env.now - queue_start
                product.total_queue_time += queue_time
                ws.queue_length -= 1

                if self.failures_enabled:
                    failure_wait_start = self.env.now
                    while ws.is_failed:
                        yield self.env.timeout(1.0)
                    failure_wait = self.env.now - failure_wait_start
                    product.total_failure_wait_time += failure_wait

                reconfig_time = self.get_reconfig_time(ws, op.op_type)
                if reconfig_time > 0:
                    yield self.env.timeout(reconfig_time)
                    product.total_reconfig_time += reconfig_time
                ws.current_setting = op.op_type

                ws.is_processing = True
                proc_time = self.get_processing_time(ws, op.op_type)
                yield self.env.timeout(proc_time)
                product.total_processing_time += proc_time
                ws.total_busy_time += proc_time
                ws.products_processed += 1
                ws.is_processing = False

            product.visited_workstations.append(ws.name)
            current_pos = ws.position
            current_zone = ws.zone
            product.current_op_index += 1

        product.exit_time = self.env.now
        self.completed_products.append(product)
        self.current_wip -= 1
        self.wip_history.append((self.env.now, self.current_wip))

    def product_generator(self, products: List[Product], inter_arrival: float):
        for product in products:
            yield self.env.timeout(self.rng.expovariate(1.0 / inter_arrival))
            self.env.process(self.process_product(product))

    def update_idle_times(self):
        for ws in self.workstations.values():
            ws.total_idle_time = self.env.now - ws.total_busy_time - ws.total_failure_time


class SimulationRunner:
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.results: List[SimulationMetrics] = []

    def run_single(self, topology: TopologyType, routing_rule: RoutingRule,
                   load_level: str, replication: int,
                   failures_enabled: bool = False,
                   variable_reconfig: bool = True,
                   verbose: bool = False) -> SimulationMetrics:

        seed = replication * 1000 + hash((topology.name, routing_rule.name, load_level)) % 1000
        start_time = time.time()

        env = simpy.Environment()

        system = ManufacturingSystem(
            env=env,
            topology=topology,
            routing_rule=routing_rule,
            config=self.config,
            seed=seed,
            failures_enabled=failures_enabled,
            variable_reconfig=variable_reconfig
        )

        product_gen = ProductGenerator(seed=seed)
        products = product_gen.generate_products(self.config.NUM_PRODUCTS)

        inter_arrival = self.config.LOAD_LEVELS[load_level]
        env.process(system.product_generator(products, inter_arrival))

        env.run(until=self.config.SIMULATION_LENGTH)

        system.update_idle_times()

        metrics = self._calculate_metrics(
            system, topology, routing_rule,
            load_level, replication,
            failures_enabled, variable_reconfig
        )
        metrics.simulation_time_sec = time.time() - start_time

        if verbose:
            self._print_metrics(metrics)

        return metrics

    def _calculate_metrics(self, system: ManufacturingSystem, topology: TopologyType,
                            routing_rule: RoutingRule, load_level: str,
                            replication: int, failures_enabled: bool,
                            variable_reconfig: bool) -> SimulationMetrics:

        completed = [p for p in system.completed_products
                     if p.entry_time >= system.config.WARMUP_PERIOD]

        if not completed:
            return SimulationMetrics(
                topology=topology.name,
                routing_rule=routing_rule.name,
                load_level=load_level,
                replication=replication,
                failures_enabled=failures_enabled,
                variable_reconfig=variable_reconfig
            )

        throughput_times = [p.exit_time - p.entry_time for p in completed]
        proc_times       = [p.total_processing_time for p in completed]
        trans_times      = [p.total_transport_time for p in completed]
        queue_times      = [p.total_queue_time for p in completed]
        reconfig_times   = [p.total_reconfig_time for p in completed]
        failure_wait_times = [p.total_failure_wait_time for p in completed]

        utilizations = []
        for ws in system.workstations.values():
            total = ws.total_busy_time + ws.total_idle_time + ws.total_failure_time
            if total > 0:
                utilizations.append(ws.total_busy_time / total * 100)

        wip_values = [w[1] for w in system.wip_history
                      if w[0] >= system.config.WARMUP_PERIOD]

        sim_hours = (system.config.SIMULATION_LENGTH - system.config.WARMUP_PERIOD) / 60
        throughput = len(completed) / sim_hours if sim_hours > 0 else 0

        total_failures = sum(ws.failure_count for ws in system.workstations.values())
        total_failure_time = sum(ws.total_failure_time for ws in system.workstations.values())
        avg_failure_time = total_failure_time / len(system.workstations) if system.workstations else 0

        total_sim_time = system.config.SIMULATION_LENGTH * len(system.workstations)
        availability = (1 - total_failure_time / total_sim_time) * 100 if total_sim_time > 0 else 100

        decisions = [d for d in system.all_routing_decisions
                     if d.timestamp >= system.config.WARMUP_PERIOD]

        avg_alternatives = np.mean([d.alternatives_count for d in decisions]) if decisions else 0

        transport_weight  = 0
        queue_weight      = 0
        processing_weight = 0
        reconfig_weight   = 0

        if decisions and routing_rule == RoutingRule.STT:
            total_scores = [d.total_score for d in decisions if d.total_score > 0]
            if total_scores:
                transport_weight  = np.mean([d.transport_time / d.total_score * 100
                                             for d in decisions if d.total_score > 0])
                queue_weight      = np.mean([d.estimated_queue_time / d.total_score * 100
                                             for d in decisions if d.total_score > 0])
                processing_weight = np.mean([d.processing_time / d.total_score * 100
                                             for d in decisions if d.total_score > 0])
                reconfig_weight   = np.mean([d.reconfig_time / d.total_score * 100
                                             for d in decisions if d.total_score > 0])

        return SimulationMetrics(
            topology=topology.name,
            routing_rule=routing_rule.name,
            load_level=load_level,
            replication=replication,
            failures_enabled=failures_enabled,
            variable_reconfig=variable_reconfig,

            avg_throughput_time=np.mean(throughput_times),
            std_throughput_time=np.std(throughput_times),
            min_throughput_time=np.min(throughput_times),
            max_throughput_time=np.max(throughput_times),

            avg_processing_time=np.mean(proc_times),
            avg_transport_time=np.mean(trans_times),
            avg_queue_time=np.mean(queue_times),
            avg_reconfig_time=np.mean(reconfig_times),
            avg_failure_wait_time=np.mean(failure_wait_times),

            avg_utilization=np.mean(utilizations) if utilizations else 0,
            min_utilization=np.min(utilizations) if utilizations else 0,
            max_utilization=np.max(utilizations) if utilizations else 0,

            total_failures=total_failures,
            avg_failure_time_per_ws=avg_failure_time,
            availability=availability,

            throughput=throughput,
            avg_wip=np.mean(wip_values) if wip_values else 0,
            products_completed=len(completed),

            avg_alternatives_considered=avg_alternatives,
            transport_weight_in_decisions=transport_weight,
            queue_weight_in_decisions=queue_weight,
            processing_weight_in_decisions=processing_weight,
            reconfig_weight_in_decisions=reconfig_weight
        )

    def _print_metrics(self, m: SimulationMetrics):
        print(f"\n{'='*70}")
        print(f"  {m.topology} | {m.routing_rule} | {m.load_level} | Rep {m.replication}")
        print(f"  Failures: {m.failures_enabled} | Variable Reconfig: {m.variable_reconfig}")
        print(f"{'='*70}")
        print(f"  Throughput Time: {m.avg_throughput_time:.1f} ± {m.std_throughput_time:.1f} min")
        print(f"    - Processing:    {m.avg_processing_time:.1f} min")
        print(f"    - Transport:     {m.avg_transport_time:.1f} min")
        print(f"    - Queue:         {m.avg_queue_time:.1f} min")
        print(f"    - Reconfig:      {m.avg_reconfig_time:.1f} min")
        print(f"    - Failure Wait:  {m.avg_failure_wait_time:.1f} min")
        print(f"  Utilization:       {m.avg_utilization:.1f}%")
        print(f"  Availability:      {m.availability:.1f}%")
        print(f"  Total Failures:    {m.total_failures}")
        print(f"  Throughput:        {m.throughput:.2f} products/hour")
        print(f"  Completed:         {m.products_completed} products")

        if m.transport_weight_in_decisions > 0:
            print(f"\n  Decision Components (STT):")
            print(f"    - Transport:   {m.transport_weight_in_decisions:.1f}%")
            print(f"    - Queue:       {m.queue_weight_in_decisions:.1f}%")
            print(f"    - Processing:  {m.processing_weight_in_decisions:.1f}%")
            print(f"    - Reconfig:    {m.reconfig_weight_in_decisions:.1f}%")


if __name__ == "__main__":
    print("Extended Competence Islands simulator")
    print("="*50)

    runner = SimulationRunner()

    print("\nTest WITHOUT failures:")
    result = runner.run_single(
        topology=TopologyType.CI,
        routing_rule=RoutingRule.STT,
        load_level='MEDIUM',
        replication=0,
        failures_enabled=False,
        variable_reconfig=True,
        verbose=True
    )

    print("\nTest WITH failures:")
    result = runner.run_single(
        topology=TopologyType.CI,
        routing_rule=RoutingRule.STT,
        load_level='MEDIUM',
        replication=0,
        failures_enabled=True,
        variable_reconfig=True,
        verbose=True
    )
