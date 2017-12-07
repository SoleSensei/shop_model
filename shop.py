import random
import simpy
import locale

AVG_ENTER_TIME = 3*60 # A customer enters every ~3 minutes
AVG_BUYS_NUBMER = 10 # A customer buys ~10 goods
SHOP_WORK_TIME = 5*60*60 # The shop works 200 minutes
NUM_TERMINAL = 1 # Number of pay terminals in the shop

# D_enter
def enter_time(): # customer entering every 'D_enter' minutes
    return random.randint(AVG_ENTER_TIME - 60, AVG_ENTER_TIME + 60)

# D_num
def buys_num(): # customer buying 'D_num' goods
    return random.randint(AVG_BUYS_NUBMER - 7, AVG_BUYS_NUBMER + 7)

# D_time
def buy_time(buys): # customer spending 'D_time' minutes buying all stuff
    time_per_one_buy = random.uniform(0.5, 2.5) * 60
    return int(buys * time_per_one_buy)

# D_pay
def pay_time(buys): # cashier spending 'D_pay' minutes on each customer
    time_per_one_buy = random.uniform(2, 5) 
    return int(buys * time_per_one_buy)

# Get current time hh::mm::ss
def format_time(stime):
    return str(stime) # just 4 test
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
    def __init__(self, env, terminals):
        self.env = env
        self.terminal = simpy.Resource(env, capacity=terminals) # shared resource
    def service(self, customer): # servicing client at cashbox
        print('%s paying his buys %s.' % (customer.name, format_time(self.env.now)))
        yield self.env.timeout( pay_time(customer.buys) )   
        print('%s payed his buys %s.' % (customer.name, format_time(self.env.now)))


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

            # Customer waits if all terminals are busy
        with self.shop.terminal.request() as request:
            yield request
            yield self.env.process(self.shop.service(self))
            print ('%s exit the shop at %s.' % (self.name, format_time(self.env.now)))
            

# Create shop and cast customers
def simmulate(env):
    # Shop creating
    print ('Shop openning at %s.' % format_time(env.now))
    terminals = NUM_TERMINAL    
    shop = Shop(env, terminals)
    
    # Customers entering the shop 
    n = 0
    while True:
        n += 1 # customer number 
        yield env.timeout( enter_time() ) # waiting for next customer enter  
        # Creating process for every customer
        env.process(Customer(env, 'Customer %d' % n, shop).shopping())
    

def main(): 
    print ('Shop simulation starts:')
    random.seed(42)
    
    # Setup process
    env = simpy.Environment()
    env.process(simmulate(env))
    
    # Execute
    env.run(until=SHOP_WORK_TIME)
    
    print ('Shop closes at %.2f.' % env.now)
    print ('Shop simulation stopped.')


if __name__ == "__main__":
    main()