import time
import serial
import threading
import sys
import queue

ser = None
def handle_data (s, data):
    data = data.strip()
    print (data)
    if data == 'LON':
        time.sleep(1)
        s.write(str.encode("MS-001- 029\r\n"))
    elif data == 'S':
        time.sleep(1)
        s.write(str.encode("G2\r\n"))
    elif data == 'H':
        time.sleep (5)
        s.write(str.encode("H\r\n"))
    elif data == 'G2':
        #time.sleep (7)
        #s.write(str.encode("R\r\n"))
        pass
    
def read_from_port(s):
    print ("Reading serial")
    while True:
        reading = s.readline().decode()
        if (len(reading) > 1):
            handle_data(s, reading)
    
def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        # Receive keyboard input from user.
        input_str = input()

        # Enqueue this input string.
        # Note: Lock not required here since we are only calling a single Queue method, not a sequence of them 
        # which would otherwise need to be treated as one atomic operation.
        inputQueue.put(input_str)

def main():
    if (len(sys.argv) == 1):
        port = 'com3'
    else:
        port = sys.argv[1]
        
    print (port)
    ser = serial.Serial(
        port=port,
        baudrate=9600,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    print (ser.port, ser.baudrate)

    if ser.isOpen():
        ser.close()
    ser.open()
    ser.isOpen()

    EXIT_COMMAND = "exit" # Command to exit this program

    # The following threading lock is required only if you need to enforce atomic access to a chunk of multiple queue
    # method calls in a row.  Use this if you have such a need, as follows:
    # 1. Pass queueLock as an input parameter to whichever function requires it.
    # 2. Call queueLock.acquire() to obtain the lock.
    # 3. Do your series of queue calls which need to be treated as one big atomic operation, such as calling
    # inputQueue.qsize(), followed by inputQueue.put(), for example.
    # 4. Call queueLock.release() to release the lock.
    # queueLock = threading.Lock() 

    #Keyboard input queue to pass data from the thread reading the keyboard inputs to the main thread.
    inputQueue = queue.Queue()

    # Create & start a thread to read keyboard inputs.
    # Set daemon to True to auto-kill this thread when all other non-daemonic threads are exited. This is desired since
    # this thread has no cleanup to do, which would otherwise require a more graceful approach to clean up then exit.
    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()

    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.start()
    # Main loop
    while (True):

        # Read keyboard inputs
        # Note: if this queue were being read in multiple places we would need to use the queueLock above to ensure
        # multi-method-call atomic access. Since this is the only place we are removing from the queue, however, in this
        # example program, no locks are required.
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()
            print("input_str = {}".format(input_str))

            if (input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                break # exit the while loop

            ser.write(str.encode(input_str+"\r\n"))
            # Insert your code here to do whatever you want with the input_str.

        # The rest of your program goes here.

        # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.1) 

    print("End.")
    ser.close()

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()
