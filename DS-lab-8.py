from multiprocessing import Process, Pipe
from os import getpid
from datetime import datetime

def local_time(counter):
    return ' (LAMPORT_TIME={}, LOCAL_TIME={})'.format(counter,
                                                      datetime.now())

def calc_recv_timestamp(recv_time_stamp, counter):
    for id  in range(len(counter)):
        counter[id] = max(recv_time_stamp[id], counter[id])
    return counter

def event(pid, counter):
    counter[pid] += 1
    print('Something happened in {} !'.\
          format(pid) + local_time(counter))
    return counter

def send_message(pipe, pid, counter, message):
    counter[pid] += 1
    pipe.send((message, counter))
    print('Message sent from ' + str(pid) + local_time(counter))
    return counter

def recv_message(pipe, pid, counter):
    message, timestamp = pipe.recv()
    counter = calc_recv_timestamp(timestamp, counter)
    print('Message received at ' + str(pid)  + local_time(counter) + " Message: " + message)
    return counter

def process_one(pipe12):
    pid = 0
    counter = [0,0,0]
    counter = send_message(pipe12, pid, counter, 'Message a1')
    counter = event(pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe12, pid, counter, 'Message a2')
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)
    counter = recv_message(pipe12, pid, counter)
    print('Process a [' + str(counter[0]) + ", " + str(counter[1]) + ", " + str(counter[2]) + "]")

def process_two(pipe21, pipe23):
    pid = 1
    counter = [0,0,0]
    counter = recv_message(pipe23, pid, counter)
    counter = recv_message(pipe23, pid, counter)
    counter = recv_message(pipe21, pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe23, pid, counter, 'Message b1')
    counter = recv_message(pipe21, pid, counter)
    counter = send_message(pipe21, pid, counter, 'Message b2')
    counter = send_message(pipe21, pid, counter, 'Message b3')
    print('Process b [' + str(counter[0]) + ", " + str(counter[1]) + ", " + str(counter[2]) + "]")

def process_three(pipe32):
    pid = 2
    counter = [0,0,0]
    counter = send_message(pipe32, pid, counter, 'Message c1')
    counter = event(pid, counter)
    counter = send_message(pipe32, pid, counter, 'Message c2')
    counter = recv_message(pipe32, pid, counter)
    print('Process c [' + str(counter[0]) + ", " + str(counter[1]) + ", " + str(counter[2]) + "]")

if __name__ == '__main__':
    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()

    processa = Process(target=process_one, 
                       args=(oneandtwo,))
    processb = Process(target=process_two, 
                       args=(twoandone, twoandthree))
    processc = Process(target=process_three, 
                       args=(threeandtwo,))

    processa.start()
    processb.start()
    processc.start()

    processa.join()
    processb.join()
    processc.join()
