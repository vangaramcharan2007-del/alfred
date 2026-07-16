class ConflictResolver:
    """
    Resolves Last-Write-Wins conflicts during sync.
    """
    def resolve(self, local_state: dict, remote_state: dict) -> dict:
        return remote_state # Trust cloud by default in this stub
