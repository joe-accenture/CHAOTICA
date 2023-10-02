class NotificationTypes():
    JOB = 0
    PHASE = 1
    SCOPING = 2
    ORGUNIT = 3
    ADMIN = 4
    SYSTEM = 5
    


# Roles that apply across the whole site with no object specific permissions
class GlobalRoles():
    ANON = 0
    ADMIN = 1
    DELIVERY_MGR = 2
    SERVICE_DELIVERY = 3
    SALES_MGR = 4
    SALES_MEMBER = 5
    USER = 6
    
    DEFAULT_ROLE = USER
    CHOICES = (
        (ANON, "Anonymous"),
        (ADMIN, "Admin"),
        (DELIVERY_MGR, "Manager"),
        (SERVICE_DELIVERY, "Service Delivery"),
        (SALES_MGR, "Sales Manager"),
        (SALES_MEMBER, "Sales Member"),
        (USER, "User"),
    )
    BS_COLOURS = (
        (ANON, "light"),
        (ADMIN, "danger"),
        (DELIVERY_MGR, "warning"),
        (SERVICE_DELIVERY, "success"),
        (SALES_MGR, "info"),
        (SALES_MEMBER, "info"),
        (USER, "secondary"),
    )
    PERMISSIONS = (
        (ANON, []),
        (ADMIN, [
            # Client
            "jobtracker.view_client", "jobtracker.add_client", "jobtracker.change_client", 
            "jobtracker.delete_client", "jobtracker.assign_account_managers_client",
            # Service
            "jobtracker.view_service", "jobtracker.add_service", "jobtracker.change_service", 
            "jobtracker.delete_service",             
            # SkillCategory
            "jobtracker.view_skillcategory", "jobtracker.add_skillcategory", 
            "jobtracker.change_skillcategory", "jobtracker.delete_skillcategory", 
            # Skill
            "jobtracker.view_skill", "jobtracker.add_skill", "jobtracker.change_skill", 
            "jobtracker.delete_skill", 'jobtracker.view_users_skill',
            # OrganisationalUnit
            "jobtracker.view_organisationalunit", "jobtracker.add_organisationalunit", "jobtracker.change_organisationalunit", 
            "jobtracker.delete_organisationalunit", 'jobtracker.assign_members_organisationalunit', 'jobtracker.view_users_schedule',
            # Certification
            "jobtracker.view_certification", "jobtracker.add_certification", "jobtracker.change_certification", 
            "jobtracker.delete_certification", 'jobtracker.view_users_certification',

        ]),
        (DELIVERY_MGR, [
            # Client
            "jobtracker.view_client", 
            # Service
            "jobtracker.view_service", "jobtracker.add_service", "jobtracker.change_service", 
            "jobtracker.delete_service", 
            # SkillCategory
            "jobtracker.view_skillcategory", "jobtracker.add_skillcategory", 
            "jobtracker.change_skillcategory", "jobtracker.delete_skillcategory", 
            # Skill
            "jobtracker.view_skill", "jobtracker.add_skill", "jobtracker.change_skill", 
            "jobtracker.delete_skill", 'jobtracker.view_users_skill',
            # OrganisationalUnit
            "jobtracker.view_organisationalunit", 'jobtracker.view_users_schedule',
            # Certification
            "jobtracker.view_certification", "jobtracker.add_certification", "jobtracker.change_certification", 
            "jobtracker.delete_certification", 'jobtracker.view_users_certification',
        ]),
        (SERVICE_DELIVERY, [
            # Client
            "jobtracker.view_client", "jobtracker.add_client", "jobtracker.change_client", 
            "jobtracker.delete_client", "jobtracker.assign_account_managers_client",
            # Service
            "jobtracker.view_service", 'jobtracker.assign_to_phase',
            # SkillCategory
            "jobtracker.view_skillcategory",
            # Skill
            "jobtracker.view_skill", 'jobtracker.view_users_skill',
            # OrganisationalUnit
            "jobtracker.view_organisationalunit", 'jobtracker.view_users_schedule',
            # Certification
            "jobtracker.view_certification", 'jobtracker.view_users_certification',
        ]),
        (SALES_MGR, [ 
            # Client
            "jobtracker.view_client", "jobtracker.add_client", "jobtracker.change_client", 
            "jobtracker.delete_client", "jobtracker.assign_account_managers_client",
            # Service
            "jobtracker.view_service",
            # SkillCategory
            "jobtracker.view_skillcategory",
            # Skill
            "jobtracker.view_skill", 'jobtracker.view_users_skill',
            # OrganisationalUnit
            "jobtracker.view_organisationalunit",
            # Certification
            "jobtracker.view_certification",
        ]),
        (SALES_MEMBER, [ 
            # Client
            "jobtracker.add_client",
            # Service
            "jobtracker.view_service",
            # SkillCategory
            "jobtracker.view_skillcategory",
            # Skill
            "jobtracker.view_skill", 'jobtracker.view_users_skill',
            # OrganisationalUnit
            "jobtracker.view_organisationalunit",
            # Certification
            "jobtracker.view_certification", 'jobtracker.view_users_certification',
        ]),
        (USER, [            
            # Service
            "jobtracker.view_service",
            # SkillCategory
            "jobtracker.view_skillcategory",
            # Skill
            "jobtracker.view_skill",
            # OrganisationalUnit
            "jobtracker.view_organisationalunit",
            # Certification
            "jobtracker.view_certification",
        ]),
    )

# These permissions are applied against specific units. Desendant jobs will use these permissions too
class UnitRoles():
    PENDING = 0
    CONSULTANT = 1
    SALES = 2
    SERVICE_DELIVERY = 3
    MANAGER = 4

    def getRolesWithPermission(permission):
        allowedAddRoles = []
        for role in UnitRoles.PERMISSIONS:
            if permission in role[1]:
                allowedAddRoles.append(role[0])
        return allowedAddRoles
    
    CHOICES = (
        (PENDING, "Pending Approval"),
        (CONSULTANT, "Consultant"),
        (SALES, "Sales"),
        (SERVICE_DELIVERY, "Service Delivery"),
        (MANAGER, "Manager"),
    )
    BS_COLOURS = (
        (PENDING, "dark"),
        (CONSULTANT, "secondary"),
        (SALES, "success"),
        (SERVICE_DELIVERY, "info"),
        (MANAGER, "danger"),
    )
    PERMISSIONS = (
        (PENDING, [
            # None
        ]),
        (CONSULTANT, [
            # Job
            # "jobtracker.view_job",
        ]),
        (SALES, [
            # Job
            "jobtracker.view_job", "jobtracker.add_job",          
        ]),
        (SERVICE_DELIVERY, [
            # OrganisationalUnit
            "jobtracker.assign_members_organisationalunit", 'jobtracker.view_users_schedule',
            # Job
            "jobtracker.view_job", "jobtracker.add_job", "jobtracker.scope_job",
        ]),
        (MANAGER, [
            # OrganisationalUnit
            "jobtracker.change_organisationalunit", "jobtracker.delete_organisationalunit",
            "jobtracker.assign_members_organisationalunit", 'jobtracker.view_users_schedule',
            # Job
            "jobtracker.view_job", "jobtracker.add_job", "jobtracker.change_job", 
            "jobtracker.delete_job", "jobtracker.scope_job",
        ]),
    )

class LeaveRequestTypes():
    ANNUAL_LEAVE = 0
    TOIL = 1
    UNPAID_LEAVE = 2
    COMPASSIONATE_LEAVE = 3
    PATERNITY_MATERNITY = 4
    JURY_SERVICE = 5
    MILITARY_LEAVE = 6
    SICK = 7
    
    CHOICES = (
        (ANNUAL_LEAVE, 'Annual leave'),
        (TOIL, 'Time Off in Lieu'),
        (UNPAID_LEAVE, 'Unpaid leave'),
        (COMPASSIONATE_LEAVE, 'Compassionate leave'),
        (PATERNITY_MATERNITY, 'Paternity/Maternity'),
        (JURY_SERVICE, 'Jury service'),
        (MILITARY_LEAVE, 'Military leave'),
        (SICK, 'Sick'),
    )