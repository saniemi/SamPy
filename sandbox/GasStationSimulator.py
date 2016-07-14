"""
Gas Station Discrete Event Simulation
=====================================

A simple discrete event simulation about a gas station operations. The gas station
has a limited number of pumps that share a common fuel reservoir. Cars randomly
arrive at the gas station, request one of the fuel pumps and start refueling from
that reservoir. The tank truck is called when the petrol level reaches a present
level (default is 10%).

The output of the simulation is written to a kafka topic. This can then be picked
up by another process.


SimPy
-----

SimPy is a discrete-event simulation library. The behavior of active components
(like vehicles, customers or messages) is modeled with processes. All processes
live in an environment. They interact with the environment and with each other
via events.


Requirements
------------

:requires: simpy (http://simpy.readthedocs.io/en/latest/)
:requires: kafka (https://github.com/dpkp/kafka-python)


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 6-Jul-2016
"""
import simpy
import simpy.rt
from kafka import KafkaProducer
import random
import itertools
import datetime
import json


# set up kafka
producer = KafkaProducer(bootstrap_servers="localhost:9092")
#producer = KafkaProducer(bootstrap_servers="localhost:9092", value_serializer=lambda m: json.dumps(m).encode('utf-8'))

def gasStation():
    """
    Gas Station Refueling example.

    Covers:

    - Resources: Resource
    - Resources: Container
    - Waiting for other processes

    Scenario:
      A gas station has a limited number of gas pumps that share a common
      fuel reservoir. Cars randomly arrive at the gas station, request one
      of the fuel pumps and start refueling from that reservoir.

      A gas station control process observes the gas station's fuel level
      and calls a tank truck for refueling if the station's level drops
      below a threshold.

    """
    RANDOM_SEED = 42
    GAS_STATION_SIZE = 500  # liters
    THRESHOLD = 10  # Threshold for calling the tank truck (in %)
    FUEL_TANK_SIZE = 50  # liters
    FUEL_TANK_LEVEL = [5, 25]  # Min/max levels of fuel tanks (in liters)
    REFUELING_SPEED = 2  # liters / second
    TANK_TRUCK_TIME = 300  # Seconds it takes the tank truck to arrive
    T_INTER = [15, 300]  # Create a car every [min, max] seconds
    SIM_TIME = 20000  # Simulation time in seconds


    def car(name, env, gas_station, fuel_pump):
        """
        A car arrives at the gas station for refueling.

        It requests one of the gas station's fuel pumps and tries to get the
        desired amount of gas from it. If the stations reservoir is
        depleted, the car has to wait for the tank truck to arrive.

        """
        fuel_tank_level = random.randint(*FUEL_TANK_LEVEL)

        txt = ('%s arriving at gas station at %.1f' % (name, env.now)).encode()
        producer.send("gasStation", txt)
        #producer.send("gasStation", {'msg': txt})

        with gas_station.request() as req:
            start = env.now
            # Request one of the gas pumps
            yield req

            # Get the required amount of fuel
            liters_required = FUEL_TANK_SIZE - fuel_tank_level
            yield fuel_pump.get(liters_required)

            # The "actual" refueling process takes some time
            yield env.timeout(liters_required / REFUELING_SPEED)

            txt = ('%s finished refueling in %.1f seconds' % (name, env.now - start)).encode()
            producer.send("gasStation", txt)
            #producer.send("gasStation", {'msg': txt})

    def gas_station_control(env, fuel_pump):
        """
        Periodically check the level of the *fuel_pump* and call the tank
        truck if the level falls below a threshold.
        """
        while True:
            if fuel_pump.level / fuel_pump.capacity * 100 < THRESHOLD:
                # We need to call the tank truck now!
                txt = ('Calling tank truck at %d' % env.now).encode()
                producer.send("gasStation", txt)
                #producer.send("gasStation", {'msg': txt})
                # Wait for the tank truck to arrive and refuel the station
                yield env.process(tank_truck(env, fuel_pump))

            yield env.timeout(10)  # Check every 10 seconds


    def tank_truck(env, fuel_pump):
        """
        Arrives at the gas station after a certain delay and refuels it.
        """
        yield env.timeout(TANK_TRUCK_TIME)

        txt = ('Tank truck arriving at time %d' % env.now).encode()
        producer.send("gasStation", txt)
        #producer.send("gasStation", {'msg': txt})

        ammount = fuel_pump.capacity - fuel_pump.level

        txt = ('Tank truck refuelling %.1f liters' % ammount).encode()
        producer.send("gasStation", txt)
        #producer.send("gasStation", {'msg': txt})

        yield fuel_pump.put(ammount)


    def car_generator(env, gas_station, fuel_pump):
        """
        Generate new cars that arrive at the gas station.
        """
        for i in itertools.count():
            yield env.timeout(random.randint(*T_INTER))
            env.process(car('Car %d' % i, env, gas_station, fuel_pump))

    # Setup and start the simulation
    txt = ('Gas Station Refuelling Simulation Started at %s' % datetime.datetime.now()).encode()
    producer.send("gasStation", txt)
    #producer.send("gasStation", {'msg': txt})

    random.seed(RANDOM_SEED)

    # Create environment and start processes
    env = simpy.rt.RealtimeEnvironment(factor=0.05)
    gas_station = simpy.Resource(env, 2)
    fuel_pump = simpy.Container(env, GAS_STATION_SIZE, init=GAS_STATION_SIZE)
    env.process(gas_station_control(env, fuel_pump))
    env.process(car_generator(env, gas_station, fuel_pump))

    # Execute
    env.run(until=SIM_TIME)


if __name__ == "__main__":
    # run the example
    gasStation()

    # push everything to the kafka cluster and close
    producer.flush()
    producer.close()
