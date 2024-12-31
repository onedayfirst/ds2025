from mpi4py import MPI
import time

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Server (Node 0)
    print("[Server] Chat Server started...")
    while True:
        print("\nOptions:")
        print("1. Broadcast Message")
        print("2. Direct Message")
        print("3. Process Peer-to-Peer Messages")
        print("4. Exit")
        action = input("Enter action (1/2/3/4): ").strip()
        
        if action == "4":
            print("[Server] Shutting down...")
            comm.bcast("exit", root=0)  # Notify all clients to exit
            break

        elif action == "1":
            message = input("[Server] Enter message to broadcast: ").strip()
            comm.bcast(message, root=0)
            print(f"[Server] Broadcasted message: {message}")

        elif action == "2":
            target_rank = int(input(f"[Server] Enter target client rank (1-{size-1}): ").strip())
            if target_rank >= size or target_rank <= 0:
                print("[Server] Invalid target rank.")
                continue
            message = input("[Server] Enter message to send directly: ").strip()
            comm.send(message, dest=target_rank, tag=1)
            print(f"[Server] Sent direct message to Client {target_rank}: {message}")

        elif action == "3":
            print("[Server] Processing peer-to-peer messages...")
            while comm.Iprobe(source=MPI.ANY_SOURCE, tag=2):
                peer_message = comm.recv(source=MPI.ANY_SOURCE, tag=2)
                try:
                    target_rank, message = peer_message.split(":", 1)
                    target_rank = int(target_rank)
                    if target_rank >= size or target_rank <= 0:
                        print("[Server] Invalid target rank specified in peer-to-peer message.")
                    else:
                        comm.send(message, dest=target_rank, tag=3)
                        print(f"[Server] Routed peer-to-peer message to Client {target_rank}: {message}")
                except ValueError:
                    print("[Server] Error processing peer-to-peer message format.")
        else:
            print("[Server] Invalid action. Please try again.")

else:
    # Client (Node 1, 2, ...)
    print(f"[Client {rank}] Client started...")
    while True:
        # Receive broadcast messages from the server
        data = comm.bcast(None, root=0)
        if data == "exit":
            print(f"[Client {rank}] Exiting as instructed by the server.")
            break
        elif data:
            print(f"[Client {rank}] Received broadcast message: {data}")
        
        # Example: Peer-to-peer messaging (manual input or predefined behavior)
        if rank == 1:  # Example: Client 1 sends a message to Client 2
            comm.send(f"2:Hi from Client {rank}!", dest=0, tag=2)  # Send message to the server
            print(f"[Client {rank}] Sent peer-to-peer message to Client 2 via Server.")
            time.sleep(2)  # Simulate delay

        # Receive peer-to-peer messages from the server
        while comm.Iprobe(source=0, tag=3):  # Check if there is a message from the server
            peer_message = comm.recv(source=0, tag=3)
            print(f"[Client {rank}] Received peer-to-peer message: {peer_message}")