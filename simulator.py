

import simpy
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import time



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
    op_type: str  # OP1, OP2, ..., OP10

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
    visited_workstations: List[str] = field(default_factory=list)

@dataclass
class Workstation:

    ws_id: int
    name: str
    ws_type: str  # A, B, C, ..., I
    competencies: List[str]  # Zoznam operácií ktoré vie robiť
    position: Tuple[int, int]  # (row, col) v mriežke
    zone: int = 0  # Pre hybrid topológiu
    

    queue_length: int = 0
    is_processing: bool = False
    current_setting: Optional[str] = None
    total_busy_time: float = 0.0
    total_idle_time: float = 0.0
    products_processed: int = 0
    

    resource: Optional[simpy.Resource] = None

@dataclass 
class SimulationMetrics:

    topology: str
    routing_rule: str
    load_level: str
    replication: int
    
    # Hlavné metriky
    avg_throughput_time: float = 0.0
    std_throughput_time: float = 0.0
    min_throughput_time: float = 0.0
    max_throughput_time: float = 0.0
    
    # Komponenty času
    avg_processing_time: float = 0.0
    avg_transport_time: float = 0.0
    avg_queue_time: float = 0.0
    avg_reconfig_time: float = 0.0
    
    # Využitie
    avg_utilization: float = 0.0
    min_utilization: float = 0.0
    max_utilization: float = 0.0
    
    # Výkon
    throughput: float = 0.0  # produkty/hodina
    avg_wip: float = 0.0
    products_completed: int = 0
    
    # Čas simulácie
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
        ('A', 'OP1'): (8.0, 1.5), ('A', 'OP2'): (10.0, 2.0),
        ('B', 'OP2'): (9.0, 1.8), ('B', 'OP3'): (11.0, 2.2),
        ('C', 'OP3'): (10.0, 2.0), ('C', 'OP4'): (12.0, 2.5),
        ('D', 'OP4'): (11.0, 2.2), ('D', 'OP5'): (13.0, 2.8),
        ('E', 'OP5'): (12.0, 2.5), ('E', 'OP6'): (14.0, 3.0), ('E', 'OP7'): (15.0, 3.2),
        ('F', 'OP6'): (13.0, 2.8), ('F', 'OP7'): (14.0, 3.0),
        ('G', 'OP7'): (13.5, 2.9), ('G', 'OP8'): (12.0, 2.5),
        ('H', 'OP8'): (11.0, 2.2), ('H', 'OP9'): (10.0, 2.0),
        ('I', 'OP9'): (9.0, 1.8), ('I', 'OP10'): (8.0, 1.5),
    }
    

    TRANSPORT_TIME_PER_UNIT = 1.0  # min
    

    RECONFIG_TIME = 3.0
    

    SIMULATION_LENGTH = 3000  # min (~2 dni)
    WARMUP_PERIOD = 300  # min
    NUM_PRODUCTS = 500  # počet produktov na vygenerovanie
    

    LOAD_LEVELS = {
        'LOW': 8.0,       # min - nízke zaťaženie
        'MEDIUM': 5.0,    # min - stredné zaťaženie
        'HIGH': 3.0       # min - vysoké zaťaženie
    }
    

    DML_ASSIGNMENT = {
        'OP1': 'A', 'OP2': 'B', 'OP3': 'C', 'OP4': 'D', 'OP5': 'E',
        'OP6': 'F', 'OP7': 'G', 'OP8': 'H', 'OP9': 'I', 'OP10': 'I'
    }
    

    HYBRID_ZONES = {
        0: ['A', 'B', 'C'],  # Zóna 1: Príprava
        1: ['D', 'E', 'F'],  # Zóna 2: Montáž
        2: ['G', 'H', 'I']   # Zóna 3: Finalizácia
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
                available = available[idx+1:]
            

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
                 routing_rule: RoutingRule, config: SystemConfig, seed: int = 42):
        self.env = env
        self.topology = topology
        self.routing_rule = routing_rule
        self.config = config
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        
        # Vytvor pracoviská
        self.workstations: Dict[str, Workstation] = {}
        self._create_workstations()
        
        # Štatistiky
        self.completed_products: List[Product] = []
        self.wip_history: List[Tuple[float, int]] = []
        self.current_wip = 0
        
        # Vstupný bod
        self.entry_position = (-1, 2)  # Pred mriežkou
        
    def _create_workstations(self):

        ws_id = 0
        for ws_type, config in self.config.WORKSTATION_TYPES.items():
            for pos in config['positions']:
                # Určenie zóny pre hybrid
                zone = 0
                for z, types in self.config.HYBRID_ZONES.items():
                    if ws_type in types:
                        zone = z
                        break
                
                # DML má vyššiu kapacitu na jednom pracovisku (ekvivalent viac staníc)
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
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:

        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_transport_time(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:

        distance = self.manhattan_distance(from_pos, to_pos)
        return distance * self.config.TRANSPORT_TIME_PER_UNIT
    
    def get_processing_time(self, ws: Workstation, op_type: str) -> float:

        key = (ws.ws_type, op_type)
        if key in self.config.PROCESSING_TIMES:
            mean, std = self.config.PROCESSING_TIMES[key]

            proc_time = self.np_rng.lognormal(np.log(mean), std/mean)
            return max(1.0, proc_time)  # Minimálne 1 min
        return 10.0  # Default
    
    def get_capable_workstations(self, op_type: str, current_zone: int = -1) -> List[Workstation]:

        capable = []
        
        for ws in self.workstations.values():
            if op_type not in ws.competencies:
                continue
                

            if self.topology == TopologyType.DML:
                if ws.ws_type != self.config.DML_ASSIGNMENT.get(op_type):
                    continue
            

            elif self.topology == TopologyType.HYBRID:
                if current_zone >= 0 and ws.zone < current_zone:
                    continue  # Nemôže ísť späť do nižšej zóny
            
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
            return capable[0]
        

        if self.routing_rule == RoutingRule.SPT:

            return min(capable, key=lambda ws: self.get_processing_time(ws, op.op_type))
        
        elif self.routing_rule == RoutingRule.SQ:

            return min(capable, key=lambda ws: ws.queue_length)
        
        elif self.routing_rule == RoutingRule.STT:

            def total_time(ws):
                transport = self.get_transport_time(current_pos, ws.position)
                queue = ws.queue_length * 10.0  # Odhadovaný čas vo fronte
                proc = self.get_processing_time(ws, op.op_type)
                reconfig = self.config.RECONFIG_TIME if ws.current_setting != op.op_type else 0
                return transport + queue + proc + reconfig
            return min(capable, key=total_time)
        
        elif self.routing_rule == RoutingRule.LB:

            def utilization(ws):
                total = ws.total_busy_time + ws.total_idle_time
                return ws.total_busy_time / total if total > 0 else 0
            return min(capable, key=utilization)
        
        elif self.routing_rule == RoutingRule.NA:

            available = [ws for ws in capable if ws.queue_length < 3]
            if not available:
                available = capable
            return min(available, key=lambda ws: self.get_transport_time(current_pos, ws.position))
        
        return capable[0]
    
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
                print(f"CHYBA: Nenájdené pracovisko pre {op.op_type}")
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
                

                if ws.current_setting != op.op_type:
                    yield self.env.timeout(self.config.RECONFIG_TIME)
                    product.total_reconfig_time += self.config.RECONFIG_TIME
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
            ws.total_idle_time = self.env.now - ws.total_busy_time




class SimulationRunner:

    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.results: List[SimulationMetrics] = []
    
    def run_single(self, topology: TopologyType, routing_rule: RoutingRule,
                   load_level: str, replication: int, verbose: bool = False) -> SimulationMetrics:

        
        seed = replication * 1000 + hash((topology.name, routing_rule.name, load_level)) % 1000
        
        start_time = time.time()
        

        env = simpy.Environment()
        

        system = ManufacturingSystem(
            env=env,
            topology=topology,
            routing_rule=routing_rule,
            config=self.config,
            seed=seed
        )
        

        product_gen = ProductGenerator(seed=seed)
        products = product_gen.generate_products(self.config.NUM_PRODUCTS)
        

        inter_arrival = self.config.LOAD_LEVELS[load_level]
        env.process(system.product_generator(products, inter_arrival))
        

        env.run(until=self.config.SIMULATION_LENGTH)
        

        system.update_idle_times()
        

        metrics = self._calculate_metrics(system, topology, routing_rule, 
                                          load_level, replication)
        metrics.simulation_time_sec = time.time() - start_time
        
        if verbose:
            self._print_metrics(metrics)
        
        return metrics
    
    def _calculate_metrics(self, system: ManufacturingSystem, topology: TopologyType,
                          routing_rule: RoutingRule, load_level: str, 
                          replication: int) -> SimulationMetrics:

        completed = [p for p in system.completed_products 
                    if p.entry_time >= system.config.WARMUP_PERIOD]
        
        if not completed:
            return SimulationMetrics(
                topology=topology.name,
                routing_rule=routing_rule.name,
                load_level=load_level,
                replication=replication
            )
        

        throughput_times = [p.exit_time - p.entry_time for p in completed]
        

        proc_times = [p.total_processing_time for p in completed]
        trans_times = [p.total_transport_time for p in completed]
        queue_times = [p.total_queue_time for p in completed]
        reconfig_times = [p.total_reconfig_time for p in completed]
        

        utilizations = []
        for ws in system.workstations.values():
            total = ws.total_busy_time + ws.total_idle_time
            if total > 0:
                utilizations.append(ws.total_busy_time / total * 100)
        

        wip_values = [w[1] for w in system.wip_history 
                     if w[0] >= system.config.WARMUP_PERIOD]
        

        sim_hours = (system.config.SIMULATION_LENGTH - system.config.WARMUP_PERIOD) / 60
        throughput = len(completed) / sim_hours if sim_hours > 0 else 0
        
        return SimulationMetrics(
            topology=topology.name,
            routing_rule=routing_rule.name,
            load_level=load_level,
            replication=replication,
            
            avg_throughput_time=np.mean(throughput_times),
            std_throughput_time=np.std(throughput_times),
            min_throughput_time=np.min(throughput_times),
            max_throughput_time=np.max(throughput_times),
            
            avg_processing_time=np.mean(proc_times),
            avg_transport_time=np.mean(trans_times),
            avg_queue_time=np.mean(queue_times),
            avg_reconfig_time=np.mean(reconfig_times),
            
            avg_utilization=np.mean(utilizations) if utilizations else 0,
            min_utilization=np.min(utilizations) if utilizations else 0,
            max_utilization=np.max(utilizations) if utilizations else 0,
            
            throughput=throughput,
            avg_wip=np.mean(wip_values) if wip_values else 0,
            products_completed=len(completed)
        )
    
    def _print_metrics(self, m: SimulationMetrics):

        print(f"\n{'='*60}")
        print(f"  {m.topology} | {m.routing_rule} | {m.load_level} | Rep {m.replication}")
        print(f"{'='*60}")
        print(f"  Throughput Time: {m.avg_throughput_time:.1f} ± {m.std_throughput_time:.1f} min")
        print(f"    - Processing:  {m.avg_processing_time:.1f} min")
        print(f"    - Transport:   {m.avg_transport_time:.1f} min")
        print(f"    - Queue:       {m.avg_queue_time:.1f} min")
        print(f"    - Reconfig:    {m.avg_reconfig_time:.1f} min")
        print(f"  Utilization:     {m.avg_utilization:.1f}% (min: {m.min_utilization:.1f}%, max: {m.max_utilization:.1f}%)")
        print(f"  Throughput:      {m.throughput:.2f} products/hour")
        print(f"  Avg WIP:         {m.avg_wip:.1f} products")
        print(f"  Completed:       {m.products_completed} products")
        print(f"  Sim Time:        {m.simulation_time_sec:.2f} sec")
