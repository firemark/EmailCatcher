from twisted.internet import reactor

if __name__ == '__main__':

    for name in ('models', 'frontend', 'smtp'):
        print("Setup %s..." % name)
        __import__(name).setup()

    print("run...")
    reactor.run()
