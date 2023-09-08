from elemental_engine import server
import platform

system = platform.system()
print(system)
if __name__ == "__main__":
    server.run("app:App", reload=True)

