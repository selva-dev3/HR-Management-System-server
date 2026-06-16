DEFAULT_PERMISSIONS = {
    'super_admin': [{'module': '*', 'actions': ['view', 'create', 'edit', 'delete', 'export', 'approve']}],
    'hr_admin': [
        {'module': 'employees', 'actions': ['view', 'create', 'edit', 'export']},
        {'module': 'recruitment', 'actions': ['view', 'create', 'edit', 'delete', 'export']},
        {'module': 'attendance', 'actions': ['view', 'create', 'edit', 'export']},
        {'module': 'leave', 'actions': ['view', 'create', 'edit', 'delete', 'export', 'approve']},
        {'module': 'payroll', 'actions': ['view', 'create', 'edit', 'export']},
        {'module': 'performance', 'actions': ['view', 'create', 'edit', 'export']},
        {'module': 'training', 'actions': ['view', 'create', 'edit', 'delete', 'export']},
        {'module': 'assets', 'actions': ['view', 'create', 'edit', 'delete', 'export']},
        {'module': 'reports', 'actions': ['view', 'export']},
        {'module': 'settings', 'actions': ['view', 'edit']},
    ],
    'manager': [
        {'module': 'employees', 'actions': ['view']},
        {'module': 'attendance', 'actions': ['view']},
        {'module': 'leave', 'actions': ['view', 'approve']},
        {'module': 'performance', 'actions': ['view', 'edit']},
    ],
    'employee': [
        {'module': 'leave', 'actions': ['view', 'create']},
        {'module': 'payroll', 'actions': ['view']},
        {'module': 'performance', 'actions': ['view']},
        {'module': 'training', 'actions': ['view', 'create']},
    ],
    'auditor': [
        {'module': 'employees', 'actions': ['view', 'export']},
        {'module': 'recruitment', 'actions': ['view', 'export']},
        {'module': 'attendance', 'actions': ['view', 'export']},
        {'module': 'leave', 'actions': ['view', 'export']},
        {'module': 'payroll', 'actions': ['view', 'export']},
        {'module': 'performance', 'actions': ['view', 'export']},
        {'module': 'training', 'actions': ['view', 'export']},
        {'module': 'assets', 'actions': ['view', 'export']},
        {'module': 'reports', 'actions': ['view', 'export']},
    ],
}


def has_permission(role: str, module: str, action: str) -> bool:
    if role == 'super_admin':
        return True
    perms = DEFAULT_PERMISSIONS.get(role, [])
    for perm in perms:
        if perm['module'] == module or perm['module'] == '*':
            if action in perm['actions']:
                return True
    return False
