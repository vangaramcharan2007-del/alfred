from jarvisx.capabilities.permission_manager import PermissionManager, PermissionLevel

def test_permission_manager():
    manager = PermissionManager()
    
    assert manager.request_permission("test_cap", PermissionLevel.READ) is True
    assert manager.check_permission("test_cap", PermissionLevel.READ) is True
    
    # Execution requires dangerous actions approval
    assert manager.request_permission("test_cap", PermissionLevel.EXECUTE) is False
    
    manager.grant_dangerous_actions()
    assert manager.request_permission("test_cap", PermissionLevel.EXECUTE) is True
    assert manager.check_permission("test_cap", PermissionLevel.EXECUTE) is True
