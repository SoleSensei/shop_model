import random
import simpy
import locale
from termcolor import cprint

AVG_ENTER_TIME = 10*60 # A customer enters every ~10 minutes
AVG_BUYS_NUBMER = 10 # A customer buys ~10 goods
SHOP_OPEN_TIME = 6*3600 # Shop opens at 6:00AM 
SHOP_CLOSE_TIME = 23*3600 # Shop closes at 11:00PM
SHOP_WORK_TIME = SHOP_CLOSE_TIME # The shop working time
NUM_TERMINAL = 2 # Number of pay terminals in the shop

# D_enter
def enter_time(): # customer entering every 'D_enter' seconds
    return random.randint(AVG_ENTER_TIME - 60, AVG_ENTER_TIME + 60)

# D_num
def buys_num(): # customer buying 'D_num' goods
    return random.randint(AVG_BUYS_NUBMER - 7, AVG_BUYS_NUBMER + 7)

# D_time
def buy_time(buys): # customer spending 'D_time' seconds buying all stuff
    time_per_one_buy = random.uniform(3, 6) * 60
    return int(buys * time_per_one_buy)

# D_pay
def pay_time(): # cashier spending 'D_pay' seconds on one buy
    time_per_one_buy = random.randint(1, 5) 
    return time_per_one_buy

# Get current time hh::mm::ss
def format_time(stime):
    # return str(stime) # just 4 test
    if (stime == 0):
        return "00:00:00"
    hours = int(stime / 3600) % 24
    minutes = int(stime % 3600 / 60)
    seconds = stime % 3600 % 60
    if (hours < 10):
        hours = "0" + str(hours)
    if (minutes < 10):
        minutes = "0" + str(minutes)
    if (seconds < 10):
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
            self.terminals.append(simpy.Resource(env, capacity=1)) # only one customer can servicing at one time 
            self.queue.append(0) # no queues at the start 
            self.cashier_speed.append(pay_time())
     
    def service(self, name, i, buys): # servicing client at cashbox
        print('%s paying his buys %s.' % (name, format_time(self.env.now)))
        service_time = self.cashier_speed[i]*buys
        yield self.env.timeout( service_time )   
        self.queue[i] -= 1
        print('%s payed his buys %s.' % (name, format_time(self.env.now)))
    
    def choose_cashbox(self, name): # customer looking for cashbox with the smallest queue
        min_quene = self.queue[0]
        min_index = 0
        for i in range(self.num_terminals):
            if (self.queue[i] < min_quene):
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
        print('%s enters shop at %s.' % (self.name, format_time(self.env.now)))
            # Customer doing buys
        yield self.env.timeout( buy_time(self.buys) )
        print ('%s finishes shopping at %s.' % (self.name, format_time(self.env.now)))

            # Customer goes to pay terminals
        yield self.env.timeout(10) # ~10 seconds to go
            # Customer goes to terminal with the smalles queue
        choosen = self.shop.choose_cashbox(self.name)

            # Customer waits if terminal is busy
        with self.shop.terminals[choosen].request() as request:
            yield request
            yield self.env.process(self.shop.service(self.name, choosen, self.buys))
            print ('%s exit the shop at %s.' % (self.name, format_time(self.env.now)))
            

# Create shop and cast customers
def simmulate(env):
    # Shop creating
    terminals = NUM_TERMINAL    
    shop = Shop(env, terminals)
    yield env.timeout( SHOP_OPEN_TIME ) # Wait for shop openning
    print ('Shop openning at %s.' % format_time(env.now))
    
    # Customers entering the shop 
    n = 0
    while True:
        n += 1 # customer number 
        yield env.timeout( enter_time() ) # waiting for next customer enter  
        # Creating process for every customer
        env.process(Customer(env, 'Customer %d' % n, shop).shopping())
    

def main(): 
    cprint ('Shop simulation starts:', 'green')
    random.seed(42)
    
    # Setup process
    env = simpy.Environment()
    env.process(simmulate(env))
    
    # Execute
    env.run(until=SHOP_WORK_TIME)
    
    print ('Shop closes at %s.' % format_time(env.now))
    cprint ('Shop simulation stopped.', 'red')


if __name__ == "__main__":
    main()