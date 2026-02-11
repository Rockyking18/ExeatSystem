# Two-Tier Admin System Implementation

## Overview
Your Django Exeat system now has a hierarchical two-tier admin structure:

1. **Django Default Admin** - Super users who manage schools and create sub-admins
2. **School Sub-Admins** - School-specific administrators who manage their school's users and resources

## System Architecture

### Models Added/Modified

#### 1. **School Model** (New)
- Represents an institution/school
- Unique school code and name
- Contact information (email, phone, address)
- One sub-admin per school (via OneToOneField)

#### 2. **SubAdmin Model** (New)
- Links a user to a school as sub-admin
- Each school has exactly one sub-admin
- Sub-admins manage all aspects of their school

#### 3. **SecurityPerson Model** (New)
- Security/gate staff for each school
- Can sign students in/out
- School-scoped visibility

#### 4. **Modified Models**
All key models now have a `school` foreign key:
- **Student** - belongs to a school
- **House** - belongs to a school (unique house names per school)
- **HouseMistress** - belongs to a school
- **Exeat** - belongs to a school
- **CustomUser** - has optional school field

## API Endpoints

### School Management (Django Admin Only)
```
POST   /api/schools/                  # Create school
GET    /api/schools/                  # List schools
PUT    /api/schools/{id}/             # Update school
DELETE /api/schools/{id}/             # Delete school
```

### Sub-Admin Management (Django Admin Only)
```
POST   /api/subadmin/create_subadmin/ # Create sub-admin for a school
```

### User Management (Admin & SubAdmin)
```
# Students
POST   /api/students/                 # Create student (school-scoped)
GET    /api/students/                 # List students (school-scoped)
PUT    /api/students/{id}/            # Update student
DELETE /api/students/{id}/            # Delete student

# House Mistresses
POST   /api/house-mistresses/         # Create house mistress (school-scoped)
GET    /api/house-mistresses/         # List house mistresses (school-scoped)
PUT    /api/house-mistresses/{id}/    # Update house mistress
DELETE /api/house-mistresses/{id}/    # Delete house mistress

# Security Personnel
POST   /api/security-personnel/       # Create security person (school-scoped)
GET    /api/security-personnel/       # List security personnel (school-scoped)
PUT    /api/security-personnel/{id}/  # Update security person
DELETE /api/security-personnel/{id}/  # Delete security person

# Houses
POST   /api/houses/                   # Create house (school-scoped)
GET    /api/houses/                   # List houses (school-scoped)
PUT    /api/houses/{id}/              # Update house
DELETE /api/houses/{id}/              # Delete house
```

### Exeat Management (All Users)
```
POST   /api/exeats/                   # Create exeat (school-scoped)
GET    /api/exeats/                   # List exeats (school-scoped)
PUT    /api/exeats/{id}/              # Update exeat
DELETE /api/exeats/{id}/              # Delete exeat

# Actions
POST   /api/exeats/{id}/approve/      # Approve exeat (admin/house mistress only)
POST   /api/exeats/{id}/reject/       # Reject exeat (admin/house mistress only)
POST   /api/exeats/{id}/sign_out/     # Sign out student (security only)
POST   /api/exeats/{id}/sign_in/      # Sign in student (security only)
```

### Dashboard
```
GET    /api/admin-dashboard/          # View exeat statistics (admin/subadmin only)
```

## Permission Model

### Django Admin (is_staff=True)
- Create and manage schools
- Create sub-admins for schools
- View all data across all schools
- Approve exeats
- Sign students in/out

### SubAdmin (has subadmin_profile)
- Manage students in their school
- Manage house mistresses in their school
- Manage security personnel in their school
- Create houses in their school
- Approve exeats in their school
- View dashboard with school statistics

### House Mistress
- View exeats for their assigned house
- Approve exeats for their house

### Security Personnel
- View exeats in their school
- Sign students out/in

### Student
- Create exeat requests
- View their own exeats

## Database Schema

```
School
  ├── Houses (one-to-many)
  ├── Students (one-to-many)
  ├── HouseMistresses (one-to-many)
  ├── SecurityPersonnel (one-to-many)
  ├── SubAdmin (one-to-one)
  └── Exeats (one-to-many)
      ├── Student (many-to-one)
      └── House (many-to-one)
```

## Usage Example

### 1. Django Admin Creates School & SubAdmin
```json
POST /api/schools/
{
  "name": "St. Mary's Secondary School",
  "code": "SMSS001",
  "email": "admin@stmarys.edu",
  "phone": "+234 123 456 7890",
  "address": "123 Main Street, Lagos"
}

POST /api/subadmin/create_subadmin/
{
  "username": "alice_admin",
  "email": "alice@stmarys.edu",
  "password": "secure_password",
  "first_name": "Alice",
  "last_name": "Johnson",
  "school_id": 1,
  "phone": "+234 123 456 7891"
}
```

### 2. SubAdmin Creates Houses
```json
POST /api/houses/
{
  "name": "Red House",
  "description": "For senior students"
}
```

### 3. SubAdmin Adds Students
```json
POST /api/students/
{
  "username": "student1",
  "email": "student1@stmarys.edu",
  "password": "student_password",
  "student_id": "S2024001",
  "name": "John Doe",
  "phone": "+234 123 456 7892",
  "house_id": 1,
  "guardian_name": "Jane Doe",
  "guardian_phone": "+234 123 456 7893"
}
```

### 4. SubAdmin Adds House Mistress
```json
POST /api/house-mistresses/
{
  "username": "mistress1",
  "email": "mistress1@stmarys.edu",
  "password": "mistress_password",
  "name": "Mrs. Smith",
  "phone": "+234 123 456 7894",
  "house_id": 1
}
```

### 5. SubAdmin Adds Security Personnel
```json
POST /api/security-personnel/
{
  "username": "security1",
  "email": "security1@stmarys.edu",
  "password": "security_password",
  "name": "Mr. Johnson",
  "phone": "+234 123 456 7895",
  "employee_id": "SEC001"
}
```

## Key Features

✅ **School Isolation** - Each school's data is completely isolated
✅ **Role-Based Access** - Users only see/manage their school's data
✅ **Scalability** - Support unlimited schools and sub-admins
✅ **Audit Trail** - Track who approved/signed students
✅ **Admin Dashboard** - View statistics per school or all schools
✅ **Flexible Exeat Status** - pending → approved → signed_out → signed_in
✅ **Email Notifications** - Integration ready for email notifications

## Admin Panel (Django Admin)

Access: `/admin/`

The admin panel now includes:
- School management
- SubAdmin management
- Student management (with school filter)
- House management (with school filter)
- HouseMistress management (with school filter)
- SecurityPerson management (with school filter)
- Exeat management (with filtering and bulk actions)

## Next Steps

1. **Email Notifications** - Send credentials when creating users
2. **OTP System** - Integrate with existing OTP model for password reset
3. **Audit Logging** - Log all critical actions
4. **Advanced Filtering** - Add date range filters to dashboard
5. **Export Reports** - Export exeat data to CSV/PDF
6. **Mobile API** - Create mobile-optimized endpoints
