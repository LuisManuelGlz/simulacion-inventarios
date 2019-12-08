import csv
from math import floor

class Simulation():
    def __init__(self, q, r):
        self.q = q # cantidad óptima a ordenar
        self.r = r # nivel óptimo de reorden
        self.initial_inventory = 150 # por defecto
        self.order_cost = 100 # por orden
        self.inventory_cost = 20 # por unidad al año
        self.missing_cost = 50 # por unidad
        self.random_numbers = []
        self.demand = []
        self.seasonal_factors = []
        self.delivery_time = []
        self.data_resolved = []

    # método que establece los primeros 12 números aleatorios
    def __set_random_numbers(self):
        count = 0

        with open('test3.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for row in csv_reader:
                if count >= 12:
                    break
                self.random_numbers.append(row[0])
                count += 1

    # método que establece la demanda
    def __set_demand(self):
        demand_file = open('demand.txt', 'r')
        
        for line in demand_file:
            data = line.strip().split(',')
            self.demand.append(data)
        
        demand_file.close()
    
    # método que establece los factores estacionales
    def __set_seasonal_factors(self):
        seasonal_factors_file = open('seasonal_factors.txt', 'r')
        
        for line in seasonal_factors_file:
            data = line.strip().split(',')
            self.seasonal_factors.append(data)
        
        seasonal_factors_file.close()

    # método que establece los tiempos de espera
    def __set_delivery_time(self):
        delivery_time_file = open('delivery_time.txt', 'r')
        
        for line in delivery_time_file:
            data = line.strip().split(',')
            self.delivery_time.append(data)
        
        delivery_time_file.close()

    def __calculate(self):
        data_month = []
        order_number_cache = 0
        delivery_time_value = 0
        missing = 0
        deliver = False
        
        for month_number in range(12):
            factor = float(self.seasonal_factors[month_number][1])
            order_number = ""
            demand_value = 0
            adjusted_demand = 0

            for demand in self.demand:
                if demand[2] < self.random_numbers[month_number] <= demand[3]:
                    demand_value = int(demand[0])
                    break
            
            adjusted_demand = floor(demand_value * factor)
            final_inventory = self.initial_inventory - adjusted_demand
            
            if final_inventory < 0:
                missing = final_inventory
                final_inventory = 0
            else:
                missing = 0

            monthly_average_inventory = floor((self.initial_inventory + final_inventory) / 2)

            if final_inventory <= self.r and delivery_time_value == 0:
                order_number_cache += 1
                order_number = order_number_cache

                for delivery_time in self.delivery_time:
                    if delivery_time[2] <= self.random_numbers[month_number] < delivery_time[3]:
                        delivery_time_value = int(delivery_time[0]) + 1
                        break

            if delivery_time_value > 0:
                delivery_time_value -= 1
                if delivery_time_value == 0:
                    deliver = True

            data_month.append([
                month_number + 1,
                self.initial_inventory,
                self.random_numbers[month_number],
                adjusted_demand,
                final_inventory,
                missing,
                order_number,
                monthly_average_inventory
            ])

            if deliver == True:
                final_inventory += self.q
                deliver = False
            
            missing = 0

            self.initial_inventory = final_inventory

        for test in data_month:
            print(test)

    #  método inicia la simulación
    def start(self):
        self.__set_random_numbers()
        self.__set_demand()
        self.__set_seasonal_factors()
        self.__set_delivery_time()
        self.__calculate()

s = Simulation(200, 100)
s.start()
# print(s.demand)
# print(s.seasonal_factors)
# print(s.delivery_time)
# print(s.random_numbers)