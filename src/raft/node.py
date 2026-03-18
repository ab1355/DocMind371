from src.raft.state_machine import ProjectState, Command
# Assuming raft_lite is available or implemented as a dependency
# import raft_lite 

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.state_machine = ProjectState()
        # self.raft = raft_lite.Raft(node_id, peers, self.apply_command)

    def apply_command(self, command_json: str):
        """
        Callback for Raft to apply a committed command.
        """
        command = Command(**json.loads(command_json))
        self.state_machine.apply(command)

    def submit_command(self, command: Command):
        """
        Submit a command to the Raft cluster.
        """
        # self.raft.submit(json.dumps(command.__dict__))
        pass
