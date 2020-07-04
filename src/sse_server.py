from flask import Flask
from flask import Response, render_template
import asyncio
import time
import threading

app = Flask(__name__)
i = 0

class TCPServer(asyncio.Protocol):    
    def connection_made(self, transport):
        self.transport = transport    
        
    def data_received(self, data):
        print("Received {data}".format(data = data.decode("utf-8")))
        #self.transport.write(data)

    def stop_server(self):
        self.transport.close()

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/sub')
def subscribe():
        def event_stream():
            global i
            while True:
                i += 1
                time.sleep(4)
                m = 'event: ping\ndata:This is event {id}.\n\n'.format(id = i)
                print("msg2: " + m)
                yield m
        return Response(event_stream(), mimetype="text/event-stream")

async def start_websocket_server():
    loop = asyncio.get_running_loop()
    server = await loop.create_server(TCPServer, "127.0.0.1", 8888)
    await server.serve_forever()

def run_t():
    asyncio.run(start_websocket_server())

if __name__ == "__main__":
    t = threading.Thread(target=run_t)
    t.start()

    app.run(debug=False)

    



