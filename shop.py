import random
import locale
import simpy
from termcolor import cprint

AVG_ENTER_TIME = 15 # A customer enters every ~25 seconds
AVG_BUYS_NUBMER = 10 # A customer buys ~10 goods
SHOP_OPEN_TIME = 6*3600 # Shop opens at 6:00AM
SHOP_CLOSE_TIME = 23*3600 # Shop closes at 11:00PM
NUM_TERMINAL = 3 # Number of pay terminals in the shop

# Statistic | Variable globals 
num_clients = 0 # Number customers in the shop right now
clients = [] # Array of clients number
timestat_c = [] # Time statistic for clients
len_queue = 0 # Queue length right now (longest)
queues = [] # Array of queue lengths
timestat_q = [] # Time statistic for queues
  

# D_enter
def enter_time(): # customer entering every 'D_enter' seconds
    return random.randint(AVG_ENTER_TIME - 15, AVG_ENTER_TIME + 15)

# D_num
def buys_num(): # customer buying 'D_num' goods
    return random.randint(AVG_BUYS_NUBMER - 7, AVG_BUYS_NUBMER + 7)

# D_time
def buy_time(buys): # customer spending 'D_time' seconds buying all stuff
    time_per_one_buy = random.uniform(3, 6) * 60 # ~3-6 minutes
    return int(buys * time_per_one_buy)

# D_pay
def pay_time(): # cashier spending 'D_pay' seconds on one buy
    time_per_one_buy = random.randint(2, 8)
    return time_per_one_buy

# Get current time hh::mm::ss
def format_time(stime):
    # return str(stime) # just 4 test
    if stime == 0:
        return "00:00:00"
    hours = int(stime / 3600) % 24
    minutes = int(stime % 3600 / 60)
    seconds = stime % 3600 % 60
    if hours < 10:
        hours = "0" + str(hours)
    if minutes < 10:
        minutes = "0" + str(minutes)
    if seconds < 10:
        seconds = "0" + str(seconds)
    return str(hours) + ":" + str(minutes) + ":" + str(seconds)


# The shop
class Shop(object):
    def __init__(self, env, num_terminals):
        self.env = env
        self.num_terminals = num_terminals
        self.terminals = [] # = cashboxes
        self.queue = [] # queue length at terminal
        self.cashier_speed = [] # cashier time per one buy
        for i in range(num_terminals):
            # Only one customer can servicing at one time
            self.terminals.append(simpy.Resource(env, capacity=1))
            self.queue.append(0) # no queues at the start
            self.cashier_speed.append(pay_time())

    def service(self, name, i, buys): # servicing client at cashbox
        print('%s paying his buys at %s.' % (name, format_time(self.env.now)))
        service_time = self.cashier_speed[i]*buys + self.cashier_speed[i]*4
        yield self.env.timeout(service_time)
        self.queue[i] -= 1
        print('%s payed his buys at %s.' % (name, format_time(self.env.now)))

    def choose_cashbox(self, name): # customer looking for cashbox with the smallest queue
        min_quene = self.queue[0]
        min_index = 0
        for i in range(self.num_terminals):
            if self.queue[i] < min_quene:
                min_quene = self.queue[i]
                min_index = i
        self.queue[min_index] += 1
        print('%s goes to terminal %d at %s.' % (name, min_index, format_time(self.env.now)))
        return min_index


# Customer shopping
class Customer(object):
    def __init__(self, env, name, shop):
        self.env = env
        self.name = name
        self.shop = shop
        self.buys = buys_num() # number of goods that customer needs

    def shopping(self):
        global clients, timestat_c, len_queue, timestat_q, queues, num_clients
        print('%s enters shop at %s.' % (self.name, format_time(self.env.now)))
        num_clients += 1
        clients.append(num_clients) # Save values for graph
        timestat_c.append(self.env.now)
            # Customer doing buys
        yield self.env.timeout(buy_time(self.buys))
        print('%s finishes shopping at %s.' % (self.name, format_time(self.env.now)))

            # Customer goes to pay terminals
        yield self.env.timeout(10) # ~10 seconds to go
            # Customer goes to terminal with the smalles queue
        choosen = self.shop.choose_cashbox(self.name)

            # Customer waits if terminal is busy
        len_queue += 1
        with self.shop.terminals[choosen].request() as request:
            yield request
            len_queue -= 1
            queues.append(len_queue) # Save values for graph
            timestat_q.append(self.env.now)
            yield self.env.process(self.shop.service(self.name, choosen, self.buys))
            print('%s exit the shop at %s.' % (self.name, format_time(self.env.now)))
            num_clients -= 1
            clients.append(num_clients)
            timestat_c.append(self.env.now)


# Create shop and cast customers
def simmulate(env):
    # Shop creating
    shop = Shop(env, NUM_TERMINAL)
    yield env.timeout(SHOP_OPEN_TIME) # Wait for shop openning
    print('Shop openning at %s.' % format_time(env.now))

    # Customers entering the shop
    num = 0 # customer number
    while SHOP_CLOSE_TIME - env.now > 60*60: # close enter one hour before closing
        num += 1
        yield env.timeout(enter_time()) # waiting for next customer enter
        # Creating process for every customer
        env.process(Customer(env, 'Customer %d' % num, shop).shopping())

def main(): 
    cprint('Shop simulation starts:', 'green')
    random.seed(42)

    # Setup process
    env = simpy.Environment()
    env.process(simmulate(env))

    # Execute
    env.run(until=SHOP_CLOSE_TIME)

    print('Shop closes at %s.' % format_time(env.now))
    cprint('Shop simulation stopped.', 'red')


if __name__ == "__main__":
    main()

from pylab import *


font = {'family' : 'Normal',
        'weight' : 'normal',
        'size'   : 22}

matplotlib.rc('font', **font)

figure()
plot(timestat_q, queues, label='queue_len')
title('Queue length')
xlabel(u'Simulation time, sec')
ylabel(u'Current queue length')
figure()
plot(timestat_c, clients)
title(u'Customers number')
xlabel(u'Simulation time, sec')
ylabel(u'Current clients number')
show()
