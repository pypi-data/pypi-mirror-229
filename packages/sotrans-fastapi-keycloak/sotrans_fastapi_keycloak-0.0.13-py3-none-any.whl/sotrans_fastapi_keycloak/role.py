class Role:
    def __init__(self, ancestors: list['Role'] | None = None, allowed_resources: list[str] | None = None):
        """Role class constructor

        Args:
            ancestors: ancestor roles with lower access level
        """
        if ancestors is None:
            ancestors = []
        if allowed_resources is None:
            allowed_resources = []

        self.ancestors = ancestors
        self.allowed_resources = allowed_resources
        self.combined_allowed_resources = self.combine_allowed_resources()

    def combine_allowed_resources(self) -> list[str]:
        """
        Combine all allowed resources from all ancestors and allowed resources of current Role.

        :return: list of all unique allowed resources
        """
        combined_allowed_resources = [*self.allowed_resources]
        for ancestor in self.ancestors:
            combined_allowed_resources.extend(ancestor.allowed_resources)
        return list(set(combined_allowed_resources))

    def check_access(self, required_role: 'Role') -> bool:
        """Check if current role satisfies access level of required role

        Args:
            required_role: role, to check if access level of current role is equal or better in hierarchy tree

        Returns: result of checking access level
        """
        return Role._check_access(required_role, self)

    @staticmethod
    def _check_access(required_role: 'Role', current_role: 'Role') -> bool:
        if current_role is required_role:
            return True
        for current_role_ancestor in current_role.ancestors:
            if Role._check_access(required_role, current_role_ancestor):
                return True
        return False
