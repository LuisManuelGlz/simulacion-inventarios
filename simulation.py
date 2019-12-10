import csv
from math import ceil

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
        self.all_costs = []
        self.random_count = 0

    # método que establece los primeros 12 números aleatorios
    def __set_random_numbers(self):
        count = 0

        with open('default.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for row in csv_reader:
                if count >= 120:
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

    # método que hace la simulación
    def __calculate(self):
        self.initial_inventory = 150
        data_month = []
        order_number_cache = 0
        delivery_time_value = 0
        missing = 0
        missing_total = 0
        missing_cache = 0
        deliver = False
        
        # para cada mes en un rango de 12
        for month_number in range(12):
            factor = float(self.seasonal_factors[month_number][1])
            order_number = ""
            demand_value = 0
            adjusted_demand = 0

            # buscamos la demanda entre los límites
            for demand in self.demand:
                if demand[2] <= self.random_numbers[self.random_count] < demand[3]:
                    demand_value = int(demand[0])
                    break
            
            adjusted_demand = ceil(demand_value * factor)
            final_inventory = self.initial_inventory - adjusted_demand
            
            # si el inventario final es negativo
            if final_inventory < 0:
                missing = final_inventory
                missing_cache += missing
                missing_total += missing_cache
                final_inventory = 0
            else:
                missing = 0
                missing_cache = 0

            monthly_average_inventory = ceil((self.initial_inventory + final_inventory) / 2)

            # si el inventario final y no está establecido una orden
            if final_inventory <= self.r and delivery_time_value == 0:
                order_number_cache += 1 # número de orden que va
                order_number = order_number_cache

                # buscamos el tiempo de llegada entre los límites
                for delivery_time in self.delivery_time:
                    if delivery_time[2] <= self.random_numbers[self.random_count] < delivery_time[3]:
                        delivery_time_value = int(delivery_time[0]) + 1
                        break

            # si hay una orden pendiente
            if delivery_time_value > 0:
                # reducimos un mes
                delivery_time_value -= 1
                # si ya pasó el tiempo establecido
                if delivery_time_value == 0:
                    # en el siguiente mes se entrega la orden
                    deliver = True

            data_month.append([
                month_number + 1,
                self.initial_inventory,
                self.random_numbers[self.random_count],
                adjusted_demand,
                final_inventory,
                missing_cache,
                order_number,
                monthly_average_inventory
            ])

            # entregamos orden (no se verá reflejado hasta que empiece el siguiente mes)
            if deliver == True:
                final_inventory += self.q
                if missing_cache < 0:
                    final_inventory += missing_cache
                deliver = False
            
            missing = 0

            self.initial_inventory = final_inventory
            self.random_count += 1

        self.data_resolved = data_month
        
        # sacamos los costos
        order_cost_final = order_number_cache * self.order_cost
        inventory_cost_final = sum(data[7] for data in self.data_resolved) * self.inventory_cost / len(self.data_resolved)
        missing_cost_final = abs(missing_total * self.missing_cost)
        total_cost_final = order_cost_final + inventory_cost_final + missing_cost_final

        self.all_costs.append([
            order_cost_final,
            self.r,
            self.q,
            inventory_cost_final,
            missing_cost_final,
            total_cost_final
        ])

        

        for data in self.data_resolved:
            print(data)
        print('--------------------')

    # método para obtener los costos
    def get_costs(self):
        flag_1 = True # bandera para que pueda mover R
        flag_2 = False # bandera para que pueda mover Q

        self.__set_random_numbers()
        self.__set_demand()
        self.__set_seasonal_factors()
        self.__set_delivery_time()

        for i in range(100):
            self.__calculate()
            self.all_costs[i].append('Sí') # por defeto será la mejor opción

            # si es primera iteración
            if i == 0:
                self.r += 25
            
            # si es la segunda en adelante hasta que se pueda operar R
            if i > 0 and flag_1:
                # si el costo total es menor al costo total anterior
                if self.all_costs[i][-2] < self.all_costs[i-1][-2]:
                    # el costo total anterior no es la mejor opción
                    self.all_costs[i-1][-1] = 'No'
                    self.r += 25
                else:
                    # el costo total actual no es la mejor opción
                    self.all_costs[i][-1] = 'No'
                    self.r -= 25
                    self.q += 25
                    flag_1 = False # deja de mover en R
                    flag_2 = True # comenzará a mover Q en la siguiente iteración
                    continue

            # si podemos mover Q
            if flag_2:
                # si el costo total es menor al costo total anterior
                if self.all_costs[i][-2] < self.all_costs[i-1][-2]:
                    # el costo total anterior no es la mejor opción
                    self.all_costs[i-1][-1] = 'No'
                    self.q += 25
                else:
                    # el costo total actual no es la mejor opción
                    self.all_costs[i][-1] = 'No'
                    # self.q -= 25
                    break

        return self.all_costs

s = Simulation(300, 500)
for sim in s.get_costs():
    print(sim)
# print(s.demand)
# print(s.seasonal_factors)
# print(s.delivery_time)
# print(s.random_numbers)