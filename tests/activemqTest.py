import stomp


class SampleListener(object):
    def on_message(self, headers, msg):
        print(msg)


conn = stomp.Connection10()
conn.set_listener('', SampleListener())
conn.start()
conn.connect()
conn.subscribe('aruba')
conn.disconnect()
