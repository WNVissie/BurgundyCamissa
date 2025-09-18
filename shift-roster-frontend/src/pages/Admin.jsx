import React, { useState, useEffect } from 'react';
import { rolesAPI, areasAPI, skillsAPI, shiftsAPI, licensesAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Shield, 
  MapPin, 
  Award, 
  Clock,
  AlertCircle,
  Settings,
  FileText
} from 'lucide-react';

export function Admin() {
  const { user, isAdmin } = useAuth();
  const [roles, setRoles] = useState([]);
  const [areas, setAreas] = useState([]);
  const [skills, setSkills] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('roles');

  // Add debug logging for user privileges
  useEffect(() => {
    console.log('Admin page - Current user:', user);
    console.log('Admin page - Is admin?', isAdmin());
    console.log('Admin page - User role:', user?.role_ref?.name);
  }, [user, isAdmin]);
  
  // Dialog states
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false);
  const [isAreaDialogOpen, setIsAreaDialogOpen] = useState(false);
  const [isSkillDialogOpen, setIsSkillDialogOpen] = useState(false);
  const [isShiftDialogOpen, setIsShiftDialogOpen] = useState(false);
  const [isLicenseDialogOpen, setIsLicenseDialogOpen] = useState(false);
  
  // Form states
  const [roleForm, setRoleForm] = useState({ name: '', description: '', permissions: {} });
  const [areaForm, setAreaForm] = useState({ name: '', description: '', color: '#808080' });
  const [skillForm, setSkillForm] = useState({ name: '', description: '', category: '' });
  const [shiftForm, setShiftForm] = useState({ name: '', start_time: '', end_time: '', hours: '', color: '#3498db' });
  const [licenseForm, setLicenseForm] = useState({ name: '', description: '' });
  
  // Editing states
  const [editingRole, setEditingRole] = useState(null);
  const [editingArea, setEditingArea] = useState(null);
  const [editingSkill, setEditingSkill] = useState(null);
  const [editingShift, setEditingShift] = useState(null);
  const [editingLicense, setEditingLicense] = useState(null);
  
  // Error states
  const [licenseError, setLicenseError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Make API calls with individual error handling
      const rolesRes = await rolesAPI.getAll();
      const areasRes = await areasAPI.getAll();
      const skillsRes = await skillsAPI.getAll();
      const shiftsRes = await shiftsAPI.getAll();
      const licensesRes = await licensesAPI.getAll();
      
      setRoles(rolesRes.data.roles || []);
      setAreas(areasRes.data.areas || []);
      setSkills(skillsRes.data.skills || []);
      setShifts(shiftsRes.data.shifts || []);
      
      // Handle licenses response structure
      const licensesData = licensesRes.data.licenses || licensesRes.data || [];
      setLicenses(licensesData);
      console.log('Licenses API response:', licensesRes.data); // Debug log
      console.log('Processed licenses data:', licensesData); // Debug log
    } catch (err) {
      console.error('Fetch error:', err); // Debug log
      
      // Try to load licenses separately if Promise.all failed
      try {
        const licensesRes = await licensesAPI.getAll();
        setLicenses(licensesRes.data || []);
        console.log('Licenses loaded separately:', licensesRes.data);
      } catch (licenseErr) {
        console.error('License API error:', licenseErr);
      }
      
      setError(err.response?.data?.error || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  // Role management
  const handleRoleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingRole) {
        await rolesAPI.update(editingRole.id, roleForm);
      } else {
        await rolesAPI.create(roleForm);
      }
      setIsRoleDialogOpen(false);
      setEditingRole(null);
      setRoleForm({ name: '', description: '', permissions: {} });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save role');
    }
  };

  const handleRoleEdit = (role) => {
    setEditingRole(role);
    setRoleForm({
      name: role.name,
      description: role.description || '',
      permissions: role.permissions || {}
    });
    setIsRoleDialogOpen(true);
  };

  const handleRoleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this role?')) {
      try {
        await rolesAPI.delete(id);
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete role');
      }
    }
  };

  // Area management
  const handleAreaSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingArea) {
        await areasAPI.update(editingArea.id, areaForm);
      } else {
        await areasAPI.create(areaForm);
      }
      setIsAreaDialogOpen(false);
      setEditingArea(null);
      setAreaForm({ name: '', description: '', color: '#808080' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save area');
    }
  };

  const handleAreaEdit = (area) => {
    setEditingArea(area);
    setAreaForm({
      name: area.name,
      description: area.description || '',
      color: area.color || '#808080'
    });
    setIsAreaDialogOpen(true);
  };

  const handleAreaDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this area?')) {
      try {
        await areasAPI.delete(id);
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete area');
      }
    }
  };

  // Skill management
  const handleSkillSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingSkill) {
        await skillsAPI.update(editingSkill.id, skillForm);
      } else {
        await skillsAPI.create(skillForm);
      }
      setIsSkillDialogOpen(false);
      setEditingSkill(null);
      setSkillForm({ name: '', description: '', category: '' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save skill');
    }
  };

  const handleSkillEdit = (skill) => {
    setEditingSkill(skill);
    setSkillForm({
      name: skill.name,
      description: skill.description || '',
      category: skill.category || ''
    });
    setIsSkillDialogOpen(true);
  };

  const handleSkillDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this skill?')) {
      try {
        await skillsAPI.delete(id);
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete skill');
      }
    }
  };

  // Shift management
  const handleShiftSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingShift) {
        await shiftsAPI.update(editingShift.id, shiftForm);
      } else {
        await shiftsAPI.create(shiftForm);
      }
      setIsShiftDialogOpen(false);
      setEditingShift(null);
  setShiftForm({ name: '', start_time: '', end_time: '', hours: '', color: '#3498db' });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save shift');
    }
  };

  const handleShiftEdit = (shift) => {
    setEditingShift(shift);
    setShiftForm({
      name: shift.name,
      start_time: shift.start_time,
      end_time: shift.end_time,
  hours: (shift.hours ?? shift.duration_hours)?.toString() || '',
  color: shift.color || '#3498db'
    });
    setIsShiftDialogOpen(true);
  };

  const handleShiftDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this shift?')) {
      try {
        await shiftsAPI.delete(id);
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete shift');
      }
    }
  };

  const handleLicenseDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this license type?')) {
      try {
        await licensesAPI.delete(id);
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete license type');
      }
    }
  };

  // License management
  const handleLicenseSubmit = async (e) => {
    e.preventDefault();
    setLicenseError(null);
    try {
      if (editingLicense) {
        await licensesAPI.update(editingLicense.id, licenseForm);
      } else {
        await licensesAPI.create(licenseForm);
      }
      setIsLicenseDialogOpen(false);
      setEditingLicense(null);
      setLicenseForm({ name: '', description: '' });
      fetchData();
    } catch (err) {
      setLicenseError(err.response?.data?.error || 'Failed to save license');
    }
  };

  const handleLicenseEdit = (license) => {
    setEditingLicense(license);
    setLicenseForm({
      name: license.name,
      description: license.description || ''
    });
    setIsLicenseDialogOpen(true);
  };

  // Fetch licenses on mount
  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600 mt-1">Manage system configuration and settings</p>
        </div>
        <div className="flex items-center space-x-2">
          <Settings className="h-5 w-5 text-gray-500" />
          <span className="text-sm text-gray-500">System Administration</span>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="roles">Roles</TabsTrigger>
          <TabsTrigger value="areas">Areas</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="shifts">Shifts</TabsTrigger>
          <TabsTrigger value="licenses">Licenses</TabsTrigger>
        </TabsList>

        {/* Roles Tab */}
        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Shield className="h-5 w-5 mr-2" />
                    Roles Management
                  </CardTitle>
                  <CardDescription>
                    Define user roles and their permissions
                  </CardDescription>
                </div>
                <Dialog open={isRoleDialogOpen} onOpenChange={setIsRoleDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => {
                      setEditingRole(null);
                      setRoleForm({ name: '', description: '', permissions: {} });
                    }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Role
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingRole ? 'Edit Role' : 'Add New Role'}
                      </DialogTitle>
                      <DialogDescription>
                        {editingRole ? 'Update role information.' : 'Create a new user role.'}
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleRoleSubmit} className="space-y-4">
                      <div>
                        <Label htmlFor="role-name">Role Name</Label>
                        <Input
                          id="role-name"
                          value={roleForm.name}
                          onChange={(e) => setRoleForm({...roleForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="role-description">Description</Label>
                        <Textarea
                          id="role-description"
                          value={roleForm.description}
                          onChange={(e) => setRoleForm({...roleForm, description: e.target.value})}
                        />
                      </div>
                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsRoleDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">
                          {editingRole ? 'Update' : 'Create'}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {roles.map((role) => (
                    <TableRow key={role.id}>
                      <TableCell>
                        <Badge variant="secondary">{role.name}</Badge>
                      </TableCell>
                      <TableCell>{role.description}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => handleRoleEdit(role)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleRoleDelete(role.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Areas Tab */}
        <TabsContent value="areas" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <MapPin className="h-5 w-5 mr-2" />
                    Areas of Responsibility
                  </CardTitle>
                  <CardDescription>
                    Define work areas and departments
                  </CardDescription>
                </div>
                <Dialog open={isAreaDialogOpen} onOpenChange={setIsAreaDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => {
                      setEditingArea(null);
                      setAreaForm({ name: '', description: '', color: '#808080' });
                    }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Area
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingArea ? 'Edit Area' : 'Add New Area'}
                      </DialogTitle>
                      <DialogDescription>
                        {editingArea ? 'Update area information.' : 'Create a new area of responsibility.'}
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleAreaSubmit} className="space-y-4">
                      <div>
                        <Label htmlFor="area-name">Area Name</Label>
                        <Input
                          id="area-name"
                          value={areaForm.name}
                          onChange={(e) => setAreaForm({...areaForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="area-color">Color</Label>
                        <Input
                          id="area-color"
                          type="color"
                          value={areaForm.color}
                          onChange={(e) => setAreaForm({...areaForm, color: e.target.value})}
                          className="w-24"
                        />
                      </div>
                      <div>
                        <Label htmlFor="area-description">Description</Label>
                        <Textarea
                          id="area-description"
                          value={areaForm.description}
                          onChange={(e) => setAreaForm({...areaForm, description: e.target.value})}
                        />
                      </div>
                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsAreaDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">
                          {editingArea ? 'Update' : 'Create'}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {areas.map((area) => (
                    <TableRow key={area.id}>
                      <TableCell>
                        <Badge variant="outline">{area.name}</Badge>
                      </TableCell>
                      <TableCell>{area.description}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => handleAreaEdit(area)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleAreaDelete(area.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Skills Tab */}
        <TabsContent value="skills" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Award className="h-5 w-5 mr-2" />
                    Skills Management
                  </CardTitle>
                  <CardDescription>
                    Define employee skills and competencies
                  </CardDescription>
                </div>
                <Dialog open={isSkillDialogOpen} onOpenChange={setIsSkillDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => {
                      setEditingSkill(null);
                      setSkillForm({ name: '', description: '', category: '' });
                    }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Skill
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingSkill ? 'Edit Skill' : 'Add New Skill'}
                      </DialogTitle>
                      <DialogDescription>
                        {editingSkill ? 'Update skill information.' : 'Create a new skill.'}
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleSkillSubmit} className="space-y-4">
                      <div>
                        <Label htmlFor="skill-name">Skill Name</Label>
                        <Input
                          id="skill-name"
                          value={skillForm.name}
                          onChange={(e) => setSkillForm({...skillForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="skill-category">Category</Label>
                        <Input
                          id="skill-category"
                          value={skillForm.category}
                          onChange={(e) => setSkillForm({...skillForm, category: e.target.value})}
                        />
                      </div>
                      <div>
                        <Label htmlFor="skill-description">Description</Label>
                        <Textarea
                          id="skill-description"
                          value={skillForm.description}
                          onChange={(e) => setSkillForm({...skillForm, description: e.target.value})}
                        />
                      </div>
                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsSkillDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">
                          {editingSkill ? 'Update' : 'Create'}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {skills.map((skill) => (
                    <TableRow key={skill.id}>
                      <TableCell>
                        <Badge>{skill.name}</Badge>
                      </TableCell>
                      <TableCell>
                        {skill.category && <Badge variant="outline">{skill.category}</Badge>}
                      </TableCell>
                      <TableCell>{skill.description}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => handleSkillEdit(skill)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleSkillDelete(skill.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Shifts Tab */}
        <TabsContent value="shifts" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Clock className="h-5 w-5 mr-2" />
                    Shift Templates
                  </CardTitle>
                  <CardDescription>
                    Define shift schedules and timings
                  </CardDescription>
                </div>
                <Dialog open={isShiftDialogOpen} onOpenChange={setIsShiftDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => {
                      setEditingShift(null);
                      setShiftForm({ name: '', start_time: '', end_time: '', hours: '', color: '#3498db' });
                    }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Shift
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingShift ? 'Edit Shift' : 'Add New Shift'}
                      </DialogTitle>
                      <DialogDescription>
                        {editingShift ? 'Update shift information.' : 'Create a new shift template.'}
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleShiftSubmit} className="space-y-4">
                      <div>
                        <Label htmlFor="shift-name">Shift Name</Label>
                        <Input
                          id="shift-name"
                          value={shiftForm.name}
                          onChange={(e) => setShiftForm({...shiftForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="start-time">Start Time</Label>
                          <Input
                            id="start-time"
                            type="time"
                            value={shiftForm.start_time}
                            onChange={(e) => setShiftForm({...shiftForm, start_time: e.target.value})}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="end-time">End Time</Label>
                          <Input
                            id="end-time"
                            type="time"
                            value={shiftForm.end_time}
                            onChange={(e) => setShiftForm({...shiftForm, end_time: e.target.value})}
                            required
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="duration">Duration (hours)</Label>
                        <Input
                          id="duration"
                          type="number"
                          step="0.5"
                          value={shiftForm.hours}
                          onChange={(e) => setShiftForm({...shiftForm, hours: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="color">Color</Label>
                        <Input
                          id="color"
                          type="color"
                          value={shiftForm.color}
                          onChange={(e) => setShiftForm({...shiftForm, color: e.target.value})}
                        />
                      </div>
                      <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => setIsShiftDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button type="submit">
                          {editingShift ? 'Update' : 'Create'}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Time</TableHead>
                    <TableHead>Color</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {shifts.map((shift) => (
                    <TableRow key={shift.id}>
                      <TableCell>
                        <Badge variant="secondary">{shift.name}</Badge>
                      </TableCell>
                      <TableCell>
                        {shift.start_time} - {shift.end_time}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <span
                            className="inline-block w-5 h-5 rounded mr-2 border"
                            style={{ backgroundColor: shift.color || '#3498db' }}
                            aria-label="Shift color"
                          />
                          <span className="text-xs text-gray-600">{shift.color || '#3498db'}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {(shift.hours ?? shift.duration_hours)} hours
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => handleShiftEdit(shift)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleShiftDelete(shift.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Licenses Tab */}
        <TabsContent value="licenses" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <FileText className="h-5 w-5 mr-2" />
                    License Types
                  </CardTitle>
                  <CardDescription>
                    Manage license types that can be assigned to employees
                  </CardDescription>
                </div>
                <Dialog open={isLicenseDialogOpen} onOpenChange={setIsLicenseDialogOpen}>
                  <DialogTrigger asChild>
                    <Button onClick={() => {
                      setEditingLicense(null);
                      setLicenseForm({ name: '', description: '' });
                    }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add License Type
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {editingLicense ? 'Edit License Type' : 'Add New License Type'}
                      </DialogTitle>
                      <DialogDescription>
                        {editingLicense ? 'Update license type information.' : 'Create a new license type.'}
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleLicenseSubmit} className="space-y-4">
                      <div>
                        <Label htmlFor="license-name">License Name</Label>
                        <Input
                          id="license-name"
                          value={licenseForm.name}
                          onChange={(e) => setLicenseForm({...licenseForm, name: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="license-description">Description</Label>
                        <Textarea
                          id="license-description"
                          value={licenseForm.description}
                          onChange={(e) => setLicenseForm({...licenseForm, description: e.target.value})}
                          placeholder="Optional description..."
                        />
                      </div>
                      <DialogFooter>
                        <Button type="submit">
                          {editingLicense ? 'Update License Type' : 'Add License Type'}
                        </Button>
                      </DialogFooter>
                      {licenseError && <div className="text-red-600">{licenseError}</div>}
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {licenses.map((license) => (
                    <TableRow key={license.id}>
                      <TableCell className="font-medium">{license.name}</TableCell>
                      <TableCell>{license.description || 'No description'}</TableCell>
                      <TableCell>{new Date(license.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleLicenseEdit(license)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm" 
                            onClick={() => handleLicenseDelete(license.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

