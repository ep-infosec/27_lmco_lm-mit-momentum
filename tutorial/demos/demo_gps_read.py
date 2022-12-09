import time # For the example only
import asyncio
import pygazebo

# What you import here depends on the message type you are subscribing to
import pygazebo.msg.v11.gps_pb2



# This is the gazebo master from PX4 message `[Msg] Connected to gazebo master @ http://127.0.0.1:11345`
HOST, PORT = "127.0.0.1", 11345


class GazeboMessageSubscriber: 

    def __init__(self, host, port, timeout=30):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.running = False
        self.timeout = timeout

    async def connect(self):
        connected = False
        for i in range(self.timeout):
            try:
                self.manager = await pygazebo.connect((self.host, self.port))
                connected = True
                break
            except Exception as e:
                print(e)
            await asyncio.sleep(1)

        if connected: 
            # info from gz topic -l, gz topic -i arg goes here
            self.gps_subscriber = self.manager.subscribe('/gazebo/default/iris_lmlidar/link/gps0',
                                                         'gazebo.msgs.GPS',
                                                         self.gps_callback)

            await self.gps_subscriber.wait_for_connection()
            self.running = True
            while self.running:
                await asyncio.sleep(0.1)
        else:
            raise Exception("Timeout connecting to Gazebo.")

    def gps_callback(self, data):
        # What *_pb2 you use here depends on the message type you are subscribing to
        self.GPS = pygazebo.msg.v11.gps_pb2.GPS()
        self.GPS.ParseFromString(data)
    
    async def get_GPS(self):
        for i in range(self.timeout):
            try:
                return self.GPS
            except Exception as e:
                # print(e)
                pass
            await asyncio.sleep(1)
    

async def run():
    gz_sub = GazeboMessageSubscriber(HOST, PORT)
    asyncio.ensure_future(gz_sub.connect())
    gps_val = await gz_sub.get_GPS()
    # Simulate doing stuff and polling for the gps values only when needed
    start = time.time()
    current_time = 0
    last_time = 0
    while (current_time < 20):
        current_time = round(time.time() - start)
        if(current_time % 5 == 0 and last_time < current_time):
            gps_val = await gz_sub.get_GPS()
            print(gps_val)
            last_time = current_time
        if(current_time % 1  == 0 and last_time < current_time):
            print(current_time)
            last_time = current_time
        # main loop needs a small sleep to yield the CPU to async activity
        await asyncio.sleep(0.01)
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
