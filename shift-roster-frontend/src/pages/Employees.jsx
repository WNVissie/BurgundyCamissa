import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { employeesAPI, rolesAPI, areasAPI, skillsAPI, designationsAPI, licensesAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { Checkbox } from '../components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../components/ui/accordion';
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
  Search, 
  Edit, 
  Trash2, 
  User, 
  Mail, 
  Phone,
  MapPin,
  Award,
  AlertCircle
} from 'lucide-react';

export function Employees() {
  const { isAdmin } = useAuth();
  const [employees, setEmployees] = useState([]);
  const [roles, setRoles] = useState([]);
  const [areas, setAreas] = useState([]);
  const [skills, setSkills] = useState([]);
  const [designations, setDesignations] = useState([]);
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  // Use non-empty sentinels for Radix Select filters
  const [selectedRole, setSelectedRole] = useState('all');
  const [selectedArea, setSelectedArea] = useState('all');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    employee_id: '',
    contact_no: '',
    email: '',
    designation_id: '',
    role_id: '',
    area_of_responsibility_id: '',
    rate_type: '',
    rate_value: '',
    total_no_leave_days_annual: ''
  });
  const [selectedSkills, setSelectedSkills] = useState([]); // array of skill IDs (string)
  const [initialSelectedSkills, setInitialSelectedSkills] = useState([]);
  const [selectedLicenses, setSelectedLicenses] = useState([]); // array of license IDs (string)
  const [licenseExpiry, setLicenseExpiry] = useState({}); // { [licenseId]: 'YYYY-MM-DD' }
  const [initialLicensesMap, setInitialLicensesMap] = useState({}); // { [licenseId]: 'YYYY-MM-DD' }

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [employeesRes, rolesRes, areasRes, skillsRes, designationsRes, licensesRes] = await Promise.all([
        employeesAPI.getAll(),
        rolesAPI.getAll(),
        areasAPI.getAll(),
        skillsAPI.getAll(),
        designationsAPI.getAll(),
        licensesAPI.getAll()
      ]);
      setEmployees(employeesRes.data.employees || []);
      setRoles(rolesRes.data.roles || []);
      setAreas(areasRes.data.areas || []);
      setSkills(skillsRes.data.skills || []);
      setDesignations(designationsRes.data || []);
      setLicenses(licensesRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingEmployee) {
        // Update logic
        const updateData = {
          email: formData.email,
          name: formData.name,
          surname: formData.surname,
          employee_id: formData.employee_id,
          contact_no: formData.contact_no,
          ...(formData.alt_contact_name ? { alt_contact_name: formData.alt_contact_name } : {}),
          ...(formData.alt_contact_no ? { alt_contact_no: formData.alt_contact_no } : {}),
          ...(formData.designation_id ? { designation_id: parseInt(formData.designation_id, 10) } : {}),
          ...(formData.role_id ? { role_id: parseInt(formData.role_id, 10) } : {}),
          ...(formData.area_of_responsibility_id ? { area_of_responsibility_id: parseInt(formData.area_of_responsibility_id, 10) } : {}),
          rate_type: formData.rate_type,
          rate_value: formData.rate_value,
          total_no_leave_days_annual: formData.total_no_leave_days_annual
        };
        console.log('Submitting annual leave days:', formData.total_no_leave_days_annual); // <-- Add this line
        await employeesAPI.update(editingEmployee.id, updateData);

        // Sync skills
        const initialSet = new Set(initialSelectedSkills.map(String));
        const currentSet = new Set(selectedSkills.map(String));
        const toAdd = [...currentSet].filter(x => !initialSet.has(x));
        const toRemove = [...initialSet].filter(x => !currentSet.has(x));
        for (const sid of toAdd) {
          await employeesAPI.addSkill(editingEmployee.id, { skill_id: parseInt(sid, 10) });
        }
        for (const sid of toRemove) {
          await employeesAPI.removeSkill(editingEmployee.id, parseInt(sid, 10));
        }

        // Sync licenses
        const initialMap = initialLicensesMap; // {id: date}
        const currentIds = new Set(selectedLicenses.map(String));
        const initialIds = new Set(Object.keys(initialMap));
        // Adds
        for (const lid of currentIds) {
          if (!initialIds.has(lid)) {
            await employeesAPI.addLicense(editingEmployee.id, { license_id: parseInt(lid, 10), expiry_date: licenseExpiry[lid] || null });
          }
        }
        // Updates
        for (const lid of currentIds) {
          if (initialIds.has(lid)) {
            const before = initialMap[lid] || null;
            const now = licenseExpiry[lid] || null;
            if (before !== now) {
              await employeesAPI.updateLicense(editingEmployee.id, parseInt(lid, 10), { expiry_date: now });
            }
          }
        }
        // Removes
        for (const lid of initialIds) {
          if (!currentIds.has(lid)) {
            await employeesAPI.removeLicense(editingEmployee.id, parseInt(lid, 10));
          }
        }
      } else {
        // Create logic
        const createData = {
          google_id: `manual_${Date.now()}`,
          email: formData.email,
          name: formData.name,
          surname: formData.surname,
          employee_id: formData.employee_id,
          contact_no: formData.contact_no,
          ...(formData.alt_contact_name ? { alt_contact_name: formData.alt_contact_name } : {}),
          ...(formData.alt_contact_no ? { alt_contact_no: formData.alt_contact_no } : {}),
          ...(formData.designation_id ? { designation_id: parseInt(formData.designation_id, 10) } : {}),
          ...(formData.role_id ? { role_id: parseInt(formData.role_id, 10) } : {}),
          ...(formData.area_of_responsibility_id ? { area_of_responsibility_id: parseInt(formData.area_of_responsibility_id, 10) } : {}),
          rate_type: formData.rate_type,
          rate_value: formData.rate_value,
          total_no_leave_days_annual: formData.total_no_leave_days_annual
        };
        const res = await employeesAPI.create(createData);
        const newId = res?.data?.employee?.id;
        if (newId) {
          // Assign skills
          for (const sid of selectedSkills) {
            await employeesAPI.addSkill(newId, { skill_id: parseInt(sid, 10) });
          }
          // Assign licenses
          for (const lid of selectedLicenses) {
            await employeesAPI.addLicense(newId, { license_id: parseInt(lid, 10), expiry_date: licenseExpiry[lid] || null });
          }
        }
      }
      
      setIsDialogOpen(false);
      setEditingEmployee(null);
      setFormData({
        name: '',
        surname: '',
        employee_id: '',
        contact_no: '',
        email: '',
        designation_id: '',
        role_id: '',
        area_of_responsibility_id: '',
        rate_type: '',
        rate_value: '',
        total_no_leave_days_annual: ''
      });
      setSelectedSkills([]);
      setInitialSelectedSkills([]);
      setSelectedLicenses([]);
      setLicenseExpiry({});
      setInitialLicensesMap({});
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save employee');
    }
  };

  const handleEdit = (employee) => {
    setEditingEmployee(employee);
    setFormData({
      name: employee.name,
      surname: employee.surname,
      employee_id: employee.employee_id,
      contact_no: employee.contact_no,
      alt_contact_name: employee.alt_contact_name || '',
      alt_contact_no: employee.alt_contact_no || '',
      email: employee.email,
      designation_id: (employee.designation_id ?? '').toString(),
      role_id: employee.role_id.toString(),
      area_of_responsibility_id: (employee.area_of_responsibility_id ?? '').toString(),
      rate_type: employee.rate_type || '',
      rate_value: employee.rate_value || '',
      total_no_leave_days_annual: employee.total_no_leave_days_annual || '' // <-- Add this line
    });
    // Skills selection
    const currentSkills = (employee.skills || []).map(s => s.id.toString());
    setSelectedSkills(currentSkills);
    setInitialSelectedSkills(currentSkills);
    // Licenses selection with expiry
    const detailed = employee.licenses_detailed || [];
    const sel = detailed.map(d => d.license_id.toString());
    setSelectedLicenses(sel);
    const exp = {};
    for (const d of detailed) {
      exp[d.license_id] = d.expiry_date || '';
    }
    setLicenseExpiry(exp);
    const initMap = {};
    for (const d of detailed) {
      initMap[d.license_id] = d.expiry_date || '';
    }
    setInitialLicensesMap(initMap);
    setIsDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await employeesAPI.delete(id);
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete employee');
      }
    }
  };

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = 
      employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.surname.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.employee_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email.toLowerCase().includes(searchTerm.toLowerCase());
    
  const matchesRole = selectedRole === 'all' || employee.role_id.toString() === selectedRole;
  const matchesArea = selectedArea === 'all' || (employee.area_of_responsibility_id?.toString() === selectedArea);
    
    return matchesSearch && matchesRole && matchesArea;
  });

  const getRoleName = (roleId) => {
    const role = roles.find(r => r.id === roleId);
    return role ? role.name : 'Unknown';
  };

  const getArea = (areaId) => {
    return areas.find(a => a.id === areaId);
  };

  // Define license options for the form
  const licenseOptions = licenses || [];

  // Helper function to check if license expires within 30 days
  const isLicenseExpiringSoon = (expiryDate) => {
    if (!expiryDate) return false;
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 30;
  };

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
          <h1 className="text-3xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-600 mt-1">Manage employee information and assignments</p>
        </div>
        
{isAdmin() && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setEditingEmployee(null);
                setFormData({
                  name: '',
                  surname: '',
                  employee_id: '',
                  contact_no: '',
                  email: '',
                  designation_id: '',
                  role_id: '',
                  area_of_responsibility_id: '',
                  rate_type: '',
                  rate_value: ''
                });
                setSelectedSkills([]);
                setInitialSelectedSkills([]);
                setSelectedLicenses([]);
                setLicenseExpiry({});
                setInitialLicensesMap({});
              }}>
                <Plus className="h-4 w-4 mr-2" />
                Add Employee
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {editingEmployee ? 'Edit Employee' : 'Add New Employee'}
                </DialogTitle>
                <DialogDescription>
                  {editingEmployee ? 'Update employee information.' : 'Add a new employee to the system.'}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4 p-2 max-h-[80vh] overflow-y-auto">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">First Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="surname">Last Name</Label>
                    <Input
                      id="surname"
                      value={formData.surname}
                      onChange={(e) => setFormData({...formData, surname: e.target.value})}
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="employee_id">Employee ID</Label>
                  <Input
                    id="employee_id"
                    value={formData.employee_id}
                    onChange={(e) => setFormData({...formData, employee_id: e.target.value})}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="contact_no">Contact Number</Label>
                  <Input
                    id="contact_no"
                    value={formData.contact_no}
                    onChange={(e) => setFormData({...formData, contact_no: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="designation">Designation</Label>
                  <Select value={formData.designation_id} onValueChange={(value) => setFormData({...formData, designation_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a designation" />
                    </SelectTrigger>
                    <SelectContent>
                      {designations.map((designation) => (
                        <SelectItem key={designation.designation_id} value={designation.designation_id.toString()}>
                          {designation.designation_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="alt_contact_name">Alternative Contact Name</Label>
                    <Input
                      id="alt_contact_name"
                      value={formData.alt_contact_name || ''}
                      onChange={(e) => setFormData({...formData, alt_contact_name: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="alt_contact_no">Alternative Contact</Label>
                    <Input
                      id="alt_contact_no"
                      value={formData.alt_contact_no || ''}
                      onChange={(e) => setFormData({...formData, alt_contact_no: e.target.value})}
                    />
                  </div>
                </div>

                <Accordion type="multiple" className="w-full">
                  <AccordionItem value="skills">
                    <AccordionTrigger>Skills</AccordionTrigger>
                    <AccordionContent>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                        {skills.map((skill) => (
                          <label key={skill.id} className="flex items-center space-x-2 text-sm">
                            <Checkbox
                              checked={selectedSkills.includes(skill.id.toString())}
                              onCheckedChange={(checked) => {
                                const id = skill.id.toString();
                                setSelectedSkills((prev) => checked ? [...prev, id] : prev.filter(s => s !== id));
                              }}
                            />
                            <span>{skill.name}</span>
                          </label>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="licenses">
                    <AccordionTrigger>Licenses</AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-4 mt-2">
                        {/* Add new license */}
                        <div className="flex flex-col sm:flex-row gap-4 p-4 border rounded-lg bg-gray-50">
                          <div className="flex-1">
                            <Label htmlFor="new-license">Add License</Label>
                            <Select onValueChange={(value) => {
                              if (value && !selectedLicenses.includes(value)) {
                                setSelectedLicenses(prev => [...prev, value]);
                              }
                            }}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select a license type" />
                              </SelectTrigger>
                              <SelectContent>
                                {licenseOptions
                                  .filter(lic => !selectedLicenses.includes(lic.id.toString()))
                                  .map((lic) => (
                                    <SelectItem key={lic.id} value={lic.id.toString()}>
                                      {lic.name}
                                    </SelectItem>
                                  ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        {/* Selected licenses */}
                        {selectedLicenses.map((licenseId) => {
                          const license = licenseOptions.find(l => l.id.toString() === licenseId);
                          if (!license) return null;
                          
                          const expiryDate = licenseExpiry[licenseId];
                          const isExpiringSoon = expiryDate && isLicenseExpiringSoon(expiryDate);
                          
                          return (
                            <div key={licenseId} className={`flex flex-col sm:flex-row sm:items-center gap-4 p-4 border rounded-lg ${isExpiringSoon ? 'bg-amber-50 border-amber-300' : 'bg-white'}`}>
                              <div className="flex items-center gap-2 flex-1">
                                <span className={`font-medium ${isExpiringSoon ? 'text-amber-700' : 'text-gray-900'}`}>
                                  {license.name}
                                </span>
                                {isExpiringSoon && (
                                  <AlertCircle className="h-4 w-4 text-amber-600" />
                                )}
                                {isExpiringSoon && (
                                  <span className="text-xs text-amber-600 font-medium">Expires soon!</span>
                                )}
                              </div>
                              
                              <div className="flex items-center gap-2">
                                <Label htmlFor={`exp_${licenseId}`} className="text-sm">Expiry Date</Label>
                                <Input
                                  id={`exp_${licenseId}`}
                                  type="date"
                                  value={licenseExpiry[licenseId] || ''}
                                  onChange={(e) => setLicenseExpiry(prev => ({...prev, [licenseId]: e.target.value}))}
                                  className={`w-40 ${isExpiringSoon ? 'border-amber-300 bg-amber-50' : ''}`}
                                />
                                <Button
                                  type="button"
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedLicenses(prev => prev.filter(id => id !== licenseId));
                                    setLicenseExpiry(prev => {
                                      const newExpiry = {...prev};
                                      delete newExpiry[licenseId];
                                      return newExpiry;
                                    });
                                  }}
                                >
                                  Remove
                                </Button>
                              </div>
                            </div>
                          );
                        })}
                        
                        {selectedLicenses.length === 0 && (
                          <p className="text-gray-500 text-sm text-center py-4">No licenses assigned. Use the dropdown above to add licenses.</p>
                        )}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                  {isAdmin() && (
                    <AccordionItem value="rates">
                      <AccordionTrigger>Rates</AccordionTrigger>
                      <AccordionContent>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="rate_type">Rate Type</Label>
                            <Select value={formData.rate_type} onValueChange={(value) => setFormData({...formData, rate_type: value})}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select a rate type" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="Monthly">Monthly</SelectItem>
                                <SelectItem value="Weekly">Weekly</SelectItem>
                                <SelectItem value="Daily">Daily</SelectItem>
                                <SelectItem value="Hourly">Hourly</SelectItem>
                                <SelectItem value="Casual">Casual</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div>
                            <Label htmlFor="rate_value">Rate Value (ZAR)</Label>
                            <Input
                              id="rate_value"
                              type="number"
                              value={formData.rate_value}
                              onChange={(e) => setFormData({...formData, rate_value: e.target.value})}
                            />
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  )}
                </Accordion>
                
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Select value={formData.role_id} onValueChange={(value) => setFormData({...formData, role_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a role" />
                    </SelectTrigger>
                    <SelectContent>
                      {roles.map((role) => (
                        <SelectItem key={role.id} value={role.id.toString()}>
                          {role.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="area">Area of Responsibility</Label>
                  <Select value={formData.area_of_responsibility_id} onValueChange={(value) => setFormData({...formData, area_of_responsibility_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select an area" />
                    </SelectTrigger>
                    <SelectContent>
                      {areas.map((area) => (
                        <SelectItem key={area.id} value={area.id.toString()}>
                          {area.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="annual-leave-days">Annual Leave Days</Label>
                  <Input
                    id="annual-leave-days"
                    type="number"
                    step="0.01"
                    value={formData.total_no_leave_days_annual || ''}
                    onChange={e => setFormData({ ...formData, total_no_leave_days_annual: e.target.value })}
                    required
                  />
                </div>

                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">
                    {editingEmployee ? 'Update' : 'Create'}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search employees..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
<Select value={selectedRole} onValueChange={setSelectedRole}>
          <SelectTrigger className="w-full md:w-48">
            <SelectValue placeholder="Filter by role" />
          </SelectTrigger>
          <SelectContent>
    <SelectItem value="all">All Roles</SelectItem>
            {roles.map((role) => (
              <SelectItem key={role.id} value={role.id.toString()}>
                {role.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
<Select value={selectedArea} onValueChange={setSelectedArea}>
          <SelectTrigger className="w-full md:w-48">
            <SelectValue placeholder="Filter by area" />
          </SelectTrigger>
          <SelectContent>
    <SelectItem value="all">All Areas</SelectItem>
            {areas.map((area) => (
              <SelectItem key={area.id} value={area.id.toString()}>
                {area.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        </div>
      </CardContent>
    </Card>

    {/* Error Alert */}
    {error && (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )}

    {/* Employees Table */}
    <Card>
      <CardHeader>
        <CardTitle>Employee List</CardTitle>
        <CardDescription>
          {filteredEmployees.length} of {employees.length} employees
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>ID</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Alt Contact Name</TableHead>
                <TableHead>Alt Contact</TableHead>
                <TableHead>Designation</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Area</TableHead>
                <TableHead>Skills</TableHead>
                {/* <TableHead>Licenses</TableHead> */}
                {isAdmin() && <TableHead>Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredEmployees.map((employee) => (
                <TableRow key={employee.id}>
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {employee.name.charAt(0)}{employee.surname.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium">{employee.name} {employee.surname}</div>
                        <div className="text-sm text-gray-500 flex items-center">
                          <Mail className="h-3 w-3 mr-1" />
                          {employee.email}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{employee.employee_id}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm flex items-center">
                      <Phone className="h-3 w-3 mr-1" />
                      {employee.contact_no}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{employee.alt_contact_name || '-'}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{employee.alt_contact_no || '-'}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{employee.designation || '-'}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">{getRoleName(employee.role_id)}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm flex items-center">
                      <MapPin className="h-3 w-3 mr-1" />
                  {(() => {
                    const area = getArea(employee.area_of_responsibility_id);
                    if (!area) return 'N/A';
                    return (
                      <Badge
                        style={{
                          backgroundColor: area.color,
                          color: 'white', // A simple choice, could be improved with a color contrast function
                        }}
                      >
                        {area.name}
                      </Badge>
                    );
                  })()}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {employee.skills?.slice(0, 2).map((skill) => (
                        <Badge key={skill.id} variant="outline" className="text-xs">
                          {skill.name}
                        </Badge>
                      ))}
                      {employee.skills?.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{employee.skills.length - 2}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  {/* <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {(employee.licenses_detailed || []).slice(0, 5).map((ld) => {
                        const soon = ld.expiring_soon;
                        const expired = ld.expired;
                        const cls = expired ? 'bg-red-100 text-red-700 border-red-300' : (soon ? 'bg-yellow-100 text-yellow-800 border-yellow-300' : '');
                        return (
                          <Badge key={ld.license_id} variant="outline" className={`text-xs ${cls}`}>
                            {(ld.license?.name || ld.name || 'License')}{ld.expiry_date ? ` (${ld.expiry_date})` : ''}
                          </Badge>
                        );
                      })}
                      {employee.licenses_detailed && employee.licenses_detailed.length > 5 && (
                        <Badge variant="outline" className="text-xs">+{employee.licenses_detailed.length - 5}</Badge>
                      )}
                    </div>
                  </TableCell> */}
                  {isAdmin() && (
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(employee)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(employee.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        {filteredEmployees.length === 0 && (
          <div className="text-center py-8">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No employees found</h3>
            <p className="text-gray-500">
              {searchTerm || selectedRole || selectedArea
                ? 'Try adjusting your search or filter criteria.'
                : 'Get started by adding your first employee.'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  </div>
);
}
