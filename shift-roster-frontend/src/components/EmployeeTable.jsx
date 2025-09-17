import React, { useState, useEffect, useMemo } from 'react';
import { employeesAPI, areasAPI, designationsAPI, skillsAPI, rosterAPI, leaveAPI } from '../lib/api';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Badge } from './ui/badge';
import { Filter, X, Users } from 'lucide-react';

export function EmployeeTable() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dropdown options
  const [areas, setAreas] = useState([]);
  const [designations, setDesignations] = useState([]);
  const [skills, setSkills] = useState([]);
  
  // Employee statuses for the selected date
  const [employeeStatuses, setEmployeeStatuses] = useState({});
  
  // Table filters
  const [filters, setFilters] = useState({
    name: '',
    area: '',
    skills: '',
    designation: '',
    date: new Date().toISOString().split('T')[0] // Default to today
  });

  // Load employees data
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        setLoading(true);
        const response = await employeesAPI.getAll();
        console.log('Employees API response:', response);
        
        // Extract data from axios response
        let employeesData = [];
        if (response && response.data && response.data.employees) {
          // Backend returns {employees: [...], total: N}
          employeesData = response.data.employees;
        } else if (response && response.data && Array.isArray(response.data)) {
          // Fallback if response.data is directly an array
          employeesData = response.data;
        } else if (Array.isArray(response)) {
          // Direct array response
          employeesData = response;
        }
        
        console.log('Processed employees data:', employeesData);
        console.log('Is array?', Array.isArray(employeesData));
        
        // Ensure we always have an array
        if (Array.isArray(employeesData)) {
          setEmployees(employeesData);
          console.log('Set employees:', employeesData.length, 'items');
        } else {
          console.warn('API response is not an array:', employeesData);
          setEmployees([]);
        }
      } catch (err) {
        console.error('Error loading employees:', err);
        setError('Failed to load employees data');
      } finally {
        setLoading(false);
      }
    };

    loadEmployees();
  }, []);

  // Load dropdown options
  useEffect(() => {
    const loadDropdownData = async () => {
      try {
        const [skillsResponse, areasResponse, designationsResponse] = await Promise.all([
          skillsAPI.getAll(),
          areasAPI.getAll(),
          designationsAPI.getAll()
        ]);
        
        console.log('Skills response:', skillsResponse);
        console.log('Areas response:', areasResponse);
        console.log('Designations response:', designationsResponse);
        
        // Extract arrays from responses, handling different response structures
        const skillsData = skillsResponse.data?.skills ? skillsResponse.data.skills : 
                          Array.isArray(skillsResponse.data) ? skillsResponse.data : 
                          Array.isArray(skillsResponse) ? skillsResponse : [];
        const areasData = areasResponse.data?.areas ? areasResponse.data.areas :
                         Array.isArray(areasResponse.data) ? areasResponse.data : 
                         Array.isArray(areasResponse) ? areasResponse : [];
        const designationsData = Array.isArray(designationsResponse.data) ? designationsResponse.data : 
                                Array.isArray(designationsResponse) ? designationsResponse : [];
        
        setSkills(skillsData);
        setAreas(areasData);
        setDesignations(designationsData);
        
        console.log('Set skills:', skillsData);
        console.log('Set areas:', areasData);
        console.log('Set designations:', designationsData);
      } catch (err) {
        console.error('Error loading dropdown data:', err);
        // Set empty arrays on error to prevent map errors
        setSkills([]);
        setAreas([]);
        setDesignations([]);
      }
    };

    loadDropdownData();
  }, []);

  // Load employee statuses for the selected date
  useEffect(() => {
    const loadEmployeeStatuses = async () => {
      if (!filters.date || employees.length === 0) {
        console.log('Skipping status load:', { date: filters.date, employeesLength: employees.length });
        return;
      }
      
      console.log('Loading employee statuses for date:', filters.date);
      
      try {
        const [rosterResponse, leaveResponse] = await Promise.all([
          rosterAPI.getAll({ start_date: filters.date, end_date: filters.date }),
          leaveAPI.getAll()
        ]);

        console.log('Roster response:', rosterResponse);
        console.log('Leave response:', leaveResponse);

        const statuses = {};
        
        // Process roster data - format: { "roster": [...], "total": 3 }
        if (rosterResponse.data?.roster && Array.isArray(rosterResponse.data.roster)) {
          rosterResponse.data.roster.forEach(roster => {
            if (roster.employee_id) {
              statuses[roster.employee_id] = {
                type: 'shift',
                details: `${roster.shift_name || 'Shift'} (${roster.start_time} - ${roster.end_time})`,
                color: 'bg-green-100 text-green-800'
              };
            }
          });
        }

        // Process leave data - format: [...]
        if (Array.isArray(leaveResponse.data)) {
          leaveResponse.data.forEach(leave => {
            if (leave.employee_id && (leave.status === 'approved' || leave.status === 'authorised')) {
              // Check if the selected date falls within the leave period
              const selectedDate = new Date(filters.date);
              const leaveStart = new Date(leave.start_date);
              const leaveEnd = new Date(leave.end_date);
              
              if (selectedDate >= leaveStart && selectedDate <= leaveEnd) {
                statuses[leave.employee_id] = {
                  type: 'leave',
                  details: `${leave.leave_type || 'Leave'}`,
                  color: 'bg-red-100 text-red-800'
                };
              }
            }
          });
        }

        console.log('Computed statuses:', statuses);
        setEmployeeStatuses(statuses);
      } catch (error) {
        console.error('Error loading employee statuses:', error);
        setEmployeeStatuses({});
      }
    };

    loadEmployeeStatuses();
  }, [filters.date, employees]);

  // Filter employees based on current filters
  const filteredEmployees = useMemo(() => {
    // Ensure employees is always an array
    if (!Array.isArray(employees)) {
      console.warn('Employees is not an array:', employees);
      return [];
    }
    
    let filtered = employees;

    // Name filter
    if (filters.name) {
      filtered = filtered.filter(emp => 
        `${emp.name || ''} ${emp.surname || ''}`.toLowerCase().includes(filters.name.toLowerCase())
      );
    }

    // Area filter
    if (filters.area && filters.area !== 'all') {
      filtered = filtered.filter(emp => 
        emp.area_of_responsibility?.name?.toLowerCase() === filters.area.toLowerCase()
      );
    }

    // Skills filter
    if (filters.skills && filters.skills !== 'all') {
      filtered = filtered.filter(emp => {
        const skillsArray = emp.skills || [];
        return skillsArray.some(skill => skill.name?.toLowerCase() === filters.skills.toLowerCase());
      });
    }

    // Designation filter
    if (filters.designation && filters.designation !== 'all') {
      filtered = filtered.filter(emp => 
        emp.designation?.toLowerCase() === filters.designation.toLowerCase()
      );
    }

    return filtered;
  }, [employees, filters]);

  // Handle filter changes
  const handleFilterChange = (column, value) => {
    // Convert "all" values back to empty strings for filtering
    const filterValue = value === 'all' ? '' : value;
    setFilters(prev => ({
      ...prev,
      [column]: filterValue
    }));
  };

  // Get employee status for selected date
  const getEmployeeStatus = (employeeId) => {
    const status = employeeStatuses[employeeId];
    if (!status) {
      return {
        type: 'available',
        details: 'Available',
        color: 'bg-blue-100 text-blue-800'
      };
    }
    return status;
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      name: '',
      area: '',
      skills: '',
      designation: '',
      date: new Date().toISOString().split('T')[0]
    });
  };

  // Check if any filters are active
  const hasActiveFilters = Object.values(filters).some(filter => filter !== '');

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="text-lg">Loading employees...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-red-500">{error}</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <CardTitle>Employee Directory</CardTitle>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline">
              {filteredEmployees.length} of {employees.length} employees
            </Badge>
            {hasActiveFilters && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={clearFilters}
                className="text-xs"
              >
                <X className="h-3 w-3 mr-1" />
                Clear Filters
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filter Row */}
        <div className="grid grid-cols-5 gap-2 mb-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Name</label>
            <Input
              placeholder="Filter by name..."
              value={filters.name}
              onChange={(e) => handleFilterChange('name', e.target.value)}
              className="h-8"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Area</label>
            <Select value={filters.area || 'all'} onValueChange={(value) => handleFilterChange('area', value)}>
              <SelectTrigger className="h-8">
                <SelectValue placeholder="All areas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All areas</SelectItem>
                {Array.isArray(areas) && areas.map((area) => (
                  <SelectItem key={area.id} value={area.name}>
                    {area.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Skills</label>
            <Select value={filters.skills || 'all'} onValueChange={(value) => handleFilterChange('skills', value)}>
              <SelectTrigger className="h-8">
                <SelectValue placeholder="All skills" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All skills</SelectItem>
                {Array.isArray(skills) && skills.map((skill) => (
                  <SelectItem key={skill.id} value={skill.name}>
                    {skill.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Designation</label>
            <Select value={filters.designation || 'all'} onValueChange={(value) => handleFilterChange('designation', value)}>
              <SelectTrigger className="h-8">
                <SelectValue placeholder="All designations" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All designations</SelectItem>
                {Array.isArray(designations) && designations.map((designation) => (
                  <SelectItem key={designation.designation_id} value={designation.designation_name}>
                    {designation.designation_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Date</label>
            <Input
              type="date"
              value={filters.date}
              onChange={(e) => handleFilterChange('date', e.target.value)}
              className="h-8"
            />
          </div>
        </div>

        {/* Results Table */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Area</TableHead>
                <TableHead>Skills</TableHead>
                <TableHead>Designation</TableHead>
                <TableHead>Status for {filters.date}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!Array.isArray(filteredEmployees) ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-red-500">
                    Error: Data is not in the expected format. Please check console for details.
                  </TableCell>
                </TableRow>
              ) : filteredEmployees.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                    {employees.length === 0 ? 'No employees found' : 'No employees match the current filters'}
                  </TableCell>
                </TableRow>
              ) : (
                filteredEmployees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{employee.name} {employee.surname}</div>
                        <div className="text-sm text-gray-500">{employee.email}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {employee.area_of_responsibility?.name || 'Not Assigned'}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {employee.skills?.length > 0 ? (
                          employee.skills.slice(0, 3).map((skill, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {skill.name}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-gray-400 text-sm">No skills</span>
                        )}
                        {employee.skills?.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{employee.skills.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {employee.designation || 'Not Set'}
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const status = getEmployeeStatus(employee.id);
                        return (
                          <Badge variant="outline" className={status.color}>
                            {status.details}
                          </Badge>
                        );
                      })()}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
