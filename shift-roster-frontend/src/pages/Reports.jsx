import React, { useState, useEffect } from 'react';
import { reportsAPI, skillsAPI, licensesAPI, rolesAPI, areasAPI, designationsAPI, employeesAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import { FileText, Search, Calendar as CalendarIcon, Filter, X } from 'lucide-react';
import { Badge } from '../components/ui/badge';
import { Popover, PopoverContent, PopoverTrigger } from '../components/ui/popover';
import { Calendar } from '../components/ui/calendar';
import { format } from 'date-fns';
import { Alert, AlertDescription } from '../components/ui/alert';
import { EmployeeTable } from '../components/EmployeeTable';
import { LeaveTable } from '../components/LeaveTable';

export function Reports() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  // State for acceptance report
  const [acceptanceReportData, setAcceptanceReportData] = useState([]);
  const [acceptanceReportLoading, setAcceptanceReportLoading] = useState(false);
  const [dateRange, setDateRange] = useState({
    from: new Date(),
    to: new Date(new Date().setDate(new Date().getDate() + 7)),
  });

  // Data for filters
  const [skills, setSkills] = useState([]);
  const [licenses, setLicenses] = useState([]);
  const [roles, setRoles] = useState([]);
  const [areas, setAreas] = useState([]);
  const [designations, setDesignations] = useState([]);

  // Selected filter values
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [selectedLicenses, setSelectedLicenses] = useState([]);
  const [selectedRoles, setSelectedRoles] = useState([]);
  const [selectedAreas, setSelectedAreas] = useState([]);
  const [selectedDesignations, setSelectedDesignations] = useState([]);
  const [searchDateRange, setSearchDateRange] = useState({
    from: new Date(),
    to: new Date(new Date().setDate(new Date().getDate() + 3)),
  });

  // State for history report
  const [allEmployees, setAllEmployees] = useState([]);
  const [selectedEmployeeForHistory, setSelectedEmployeeForHistory] = useState('');
  const [historyReport, setHistoryReport] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  // TEMPORARILY REMOVED - Leave report state variables
  // const [leaveReport, setLeaveReport] = useState(null);
  // const [leaveReportLoading, setLeaveReportLoading] = useState(false);
  // const [leaveFilters, setLeaveFilters] = useState({
  //   employee_id: '',
  //   status: '',
  //   leave_type: '',
  //   start_date: '',
  //   end_date: ''
  // });


  useEffect(() => {
    // Fetch data for populating filter dropdowns
    const fetchFilterData = async () => {
      try {
        console.log('Starting to fetch filter data...');
        const [skillsRes, licensesRes, rolesRes, areasRes, designationsRes, employeesRes] = await Promise.all([
          skillsAPI.getAll(),
          licensesAPI.getAll(),
          rolesAPI.getAll(),
          areasAPI.getAll(),
          designationsAPI.getAll(),
          employeesAPI.getAll(),
        ]);
        
        console.log('API responses:', {
          skills: skillsRes.data,
          licenses: licensesRes.data,
          roles: rolesRes.data,
          areas: areasRes.data,
          designations: designationsRes.data,
          employees: employeesRes.data
        });
        
        const skillsData = Array.isArray(skillsRes.data?.skills) ? skillsRes.data.skills : 
                          Array.isArray(skillsRes.data) ? skillsRes.data : [];
        const licensesData = (Array.isArray(licensesRes.data?.licenses) ? licensesRes.data.licenses : 
                             Array.isArray(licensesRes.data) ? licensesRes.data : [])
                             .map(l => ({ id: l.id, name: l.name })).filter(l => l.id && l.name);
        const rolesData = Array.isArray(rolesRes.data?.roles) ? rolesRes.data.roles : 
                         Array.isArray(rolesRes.data) ? rolesRes.data : [];
        const areasData = Array.isArray(areasRes.data?.areas) ? areasRes.data.areas : 
                         Array.isArray(areasRes.data) ? areasRes.data : [];
        const designationsData = (Array.isArray(designationsRes.data?.designations) ? designationsRes.data.designations : 
                                 Array.isArray(designationsRes.data) ? designationsRes.data : [])
                                 .map(d => ({ 
                                   id: d.designation_id || d.id, 
                                   name: d.designation_name || d.name 
                                 })).filter(d => d.id && d.name);
        const employeesData = Array.isArray(employeesRes.data?.employees) ? employeesRes.data.employees : 
                             Array.isArray(employeesRes.data) ? employeesRes.data : [];
        
        console.log('Processed filter data:', {
          skills: skillsData,
          licenses: licensesData,
          roles: rolesData,
          areas: areasData,
          designations: designationsData,
          employees: employeesData
        });
        
        setSkills(skillsData);
        setLicenses(licensesData);
        setRoles(rolesData);
        setAreas(areasData);
        setDesignations(designationsData);
        setAllEmployees(employeesData);
        
        console.log('Filter data loaded successfully');
      } catch (err) {
        console.error('Error fetching filter data:', err);
        setError(`Failed to load filter options: ${err.message}`);
        // Set empty arrays as fallbacks
        setSkills([]);
        setLicenses([]);
        setRoles([]);
        setAreas([]);
        setDesignations([]);
        setAllEmployees([]);
      }
    };
    fetchFilterData();
  }, []);

  const handleSearch = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        skill_ids: selectedSkills,
        license_ids: selectedLicenses,
        role_ids: selectedRoles,
        area_ids: selectedAreas,
        designation_ids: selectedDesignations,
        start_date: searchDateRange.from ? format(searchDateRange.from, 'yyyy-MM-dd') : undefined,
        end_date: searchDateRange.to ? format(searchDateRange.to, 'yyyy-MM-dd') : undefined,
      };
      console.log('Selected filters:');
      console.log('  Skills:', selectedSkills);
      console.log('  Licenses:', selectedLicenses);
      console.log('  Roles:', selectedRoles);
      console.log('  Areas:', selectedAreas);
      console.log('  Designations:', selectedDesignations);
      console.log('Calling employee search with params:', params);
      const res = await reportsAPI.employeeSearch(params);
      console.log('Raw response:', res);
      console.log('Response data:', res.data);
      setSearchResults(res.data.results || res.data || []);
      console.log('Employee search results:', res.data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.error || 'Failed to perform search.');
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySearch = async () => {
    if (!selectedEmployeeForHistory) return;
    try {
      setHistoryLoading(true);
      setError(null);
      const res = await reportsAPI.getEmployeeHistory(selectedEmployeeForHistory);
      setHistoryReport(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch history report.');
      setHistoryReport(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleAcceptanceReportSearch = async () => {
    try {
      setAcceptanceReportLoading(true);
      setError(null);
      const params = {
        start_date: dateRange.from ? format(dateRange.from, 'yyyy-MM-dd') : undefined,
        end_date: dateRange.to ? format(dateRange.to, 'yyyy-MM-dd') : undefined,
      };
      const res = await reportsAPI.shiftAcceptance(params);
      setAcceptanceReportData(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate acceptance report.');
      setAcceptanceReportData([]);
    } finally {
      setAcceptanceReportLoading(false);
    }
  };

  // TEMPORARILY REMOVED - Leave report functions
  // const handleLeaveReportSearch = async () => { ... }
  // const handleExportLeaveReport = async () => { ... }

  const FilterCheckboxGroup = ({ title, items, selectedItems, setSelectedItems }) => (
    <div className="p-4 border rounded-lg">
      <h4 className="font-semibold mb-2">{title}</h4>
      <div className="max-h-40 overflow-y-auto space-y-2">
        {items.map(item => (
          <label key={item.id} className="flex items-center space-x-2 text-sm">
            <Checkbox
              checked={selectedItems.includes(item.id)}
              onCheckedChange={(checked) => {
                console.log(`${title} checkbox changed:`, {
                  itemId: item.id,
                  itemName: item.name || item.role_name || item.designation_name,
                  checked: checked,
                  currentSelection: selectedItems
                });
                setSelectedItems(prev => {
                  const newSelection = checked ? [...prev, item.id] : prev.filter(id => id !== item.id);
                  console.log(`${title} new selection:`, newSelection);
                  return newSelection;
                });
              }}
            />
            <span>{item.name || item.role_name || item.designation_name}</span>
          </label>
        ))}
      </div>
    </div>
  );

  const safeAcceptanceReportData = Array.isArray(acceptanceReportData) ? acceptanceReportData : [];

  return (
    <div className="space-y-6">
      {/* Employee Directory with Table Filters - WORKING SOLUTION */}
      <EmployeeTable />

      {/* Original Advanced Employee Report - Keep for reference */}
      <Card style={{ display: 'none' }}>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Advanced Employee Report
          </CardTitle>
          <CardDescription>
            Find employees based on their skills, licenses, roles, and more.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <FilterCheckboxGroup title="Skills" items={skills} selectedItems={selectedSkills} setSelectedItems={setSelectedSkills} />
            <FilterCheckboxGroup title="Licenses" items={licenses} selectedItems={selectedLicenses} setSelectedItems={setSelectedLicenses} />
            <FilterCheckboxGroup title="Roles" items={roles} selectedItems={selectedRoles} setSelectedItems={setSelectedRoles} />
            <FilterCheckboxGroup title="Areas" items={areas} selectedItems={selectedAreas} setSelectedItems={setSelectedAreas} />
            <FilterCheckboxGroup title="Designations" items={designations} selectedItems={selectedDesignations} setSelectedItems={setSelectedDesignations} />
          </div>
          
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="w-auto">
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {searchDateRange?.from ? (
                      searchDateRange.to ? (
                        <>
                          {format(searchDateRange.from, 'LLL dd, y')} - {format(searchDateRange.to, 'LLL dd, y')}
                        </>
                      ) : (
                        format(searchDateRange.from, 'LLL dd, y')
                      )
                    ) : (
                      <span>Pick date range</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={searchDateRange?.from}
                    selected={searchDateRange}
                    onSelect={setSearchDateRange}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            </div>
            
            <div className="pt-6">
              <Button onClick={handleSearch} disabled={loading}>
                <Search className="h-4 w-4 mr-2" />
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>
          </div>
          
          {searchResults && Array.isArray(searchResults) && searchResults.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-4">Search Results</h4>
              {searchResults.map((dateGroup, index) => (
                <div key={index} className="mb-6 border rounded-lg p-4">
                  <h5 className="font-semibold text-lg mb-3 text-blue-700">
                    {dateGroup.date} ({dateGroup.total_count} employee(s))
                  </h5>
                  {dateGroup.employees && dateGroup.employees.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Employee</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Area</TableHead>
                          <TableHead>Skills</TableHead>
                          <TableHead>Licenses</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {dateGroup.employees.map(employee => (
                          <TableRow key={employee.id}>
                            <TableCell>{employee.name} {employee.surname}</TableCell>
                            <TableCell>{employee.role?.name || employee.role?.role_name || 'N/A'}</TableCell>
                            <TableCell>{employee.area_of_responsibility?.name || employee.area?.name || 'N/A'}</TableCell>
                            <TableCell>
                              {employee.skills?.map(skill => skill.name).join(', ') || 'None'}
                            </TableCell>
                            <TableCell>
                              {employee.licenses?.map(license => license.name).join(', ') || 'None'}
                            </TableCell>
                            <TableCell>
                              <Badge variant={
                                employee.current_status === 'Available' ? 'success' : 
                                employee.current_status?.includes('On Shift') ? 'default' :
                                employee.current_status?.includes('On Leave') ? 'destructive' : 'secondary'
                              }>
                                {employee.current_status || 'Unknown'}
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <p className="text-gray-500 italic">No employees found for this date with the selected criteria.</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}

      <Card>
        <CardHeader>
          <CardTitle>Shift Acceptance Report</CardTitle>
          <CardDescription>View who has accepted their shifts for a given period.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-auto">
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateRange?.from ? (
                    dateRange.to ? (
                      <>
                        {format(dateRange.from, 'LLL dd, y')} - {format(dateRange.to, 'LLL dd, y')}
                      </>
                    ) : (
                      format(dateRange.from, 'LLL dd, y')
                    )
                  ) : (
                    <span>Pick a date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  initialFocus
                  mode="range"
                  defaultMonth={dateRange?.from}
                  selected={dateRange}
                  onSelect={setDateRange}
                  numberOfMonths={2}
                />
              </PopoverContent>
            </Popover>
            <Button onClick={handleAcceptanceReportSearch} disabled={acceptanceReportLoading}>
              {acceptanceReportLoading ? 'Generating...' : 'Generate Report'}
            </Button>
          </div>
          {safeAcceptanceReportData.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Shift</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Approved By</TableHead>
                  <TableHead>Approved Time</TableHead>
                  <TableHead>Accepted Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {safeAcceptanceReportData.map(entry => (
                  <TableRow key={entry.id}>
                    <TableCell>{entry.employee?.name} {entry.employee?.surname}</TableCell>
                    <TableCell>{entry.date}</TableCell>
                    <TableCell>{entry.shift?.name}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          entry.status === 'accepted' ? 'success' : 
                          entry.status === 'approved' ? 'default' : 
                          entry.status === 'pending' ? 'warning' :
                          entry.status === 'rejected' ? 'destructive' : 'secondary'
                        }
                        className={
                          entry.status === 'accepted' ? 'bg-green-500 text-white' : 
                          entry.status === 'approved' ? 'bg-blue-500 text-white' : 
                          entry.status === 'pending' ? 'bg-amber-500 text-white' :
                          entry.status === 'rejected' ? 'bg-red-500 text-white' : ''
                        }
                      >
                        {entry.status || 'pending'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {entry.approver ? `${entry.approver.name} ${entry.approver.surname}` : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {entry.approved_at ? new Date(entry.approved_at).toLocaleString() : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {entry.accepted_at ? new Date(entry.accepted_at).toLocaleString() : 'N/A'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Employee History Report</CardTitle>
          <CardDescription>View the complete shift history for a single employee.</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center space-x-2">
          <Select onValueChange={setSelectedEmployeeForHistory} value={selectedEmployeeForHistory}>
            <SelectTrigger className="w-[280px]">
              <SelectValue placeholder="Select an employee" />
            </SelectTrigger>
            <SelectContent>
              {allEmployees.filter(emp => emp && emp.id).map(emp => (
                <SelectItem key={emp.id} value={emp.id.toString()}>
                  {emp.name || emp.first_name || 'Unknown'} {emp.surname || emp.last_name || ''} ({emp.employee_id || emp.id})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={handleHistorySearch} disabled={historyLoading || !selectedEmployeeForHistory}>
            {historyLoading ? 'Loading...' : 'View History'}
          </Button>
        </CardContent>
        {historyReport && historyReport.employee_details && (
          <CardContent>
            <h3 className="font-bold text-lg mb-2">History for {historyReport.employee_details?.name} {historyReport.employee_details?.surname}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="p-4 bg-gray-100 rounded-lg">
                <p className="text-sm font-medium text-gray-600">Total Shifts</p>
                <p className="text-2xl font-bold">{historyReport.summary?.total_shifts || 0}</p>
              </div>
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Shift</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Shift Status</TableHead>
                  <TableHead>Timesheet Status</TableHead>
                  <TableHead>Timesheet Notes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(historyReport.shift_history || []).map(entry => (
                  <TableRow key={entry.id}>
                    <TableCell>{entry.date}</TableCell>
                    <TableCell>{entry.shift?.name || 'N/A'}</TableCell>
                    <TableCell>{entry.hours}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          entry.status === 'accepted' ? 'success' : 
                          entry.status === 'approved' ? 'default' : 
                          entry.status === 'pending' ? 'warning' :
                          entry.status === 'rejected' ? 'destructive' : 'secondary'
                        }
                        className={
                          entry.status === 'accepted' ? 'bg-green-500 text-white' : 
                          entry.status === 'approved' ? 'bg-blue-500 text-white' : 
                          entry.status === 'pending' ? 'bg-amber-500 text-white' :
                          entry.status === 'rejected' ? 'bg-red-500 text-white' : ''
                        }
                      >
                        {entry.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {entry.timesheet ? (
                        <Badge variant={entry.timesheet.status === 'approved' ? 'success' : entry.timesheet.status === 'rejected' ? 'destructive' : 'secondary'}>
                          {entry.timesheet.status}
                        </Badge>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                    <TableCell>{entry.timesheet?.notes || ''}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        )}
      </Card>

      {/* TEMPORARILY DISABLED - Leave Report Card with filters causing issues */}
      {/*
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Leave Report
          </CardTitle>
          <CardDescription>
            Comprehensive leave analytics with filtering and export options.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center p-8">
            <p className="text-gray-500">Leave Report temporarily disabled for maintenance.</p>
          </div>
        </CardContent>
      </Card>
      */}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Leave Directory
          </CardTitle>
          <CardDescription>
            View all leave requests in the system.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LeaveTable />
        </CardContent>
      </Card>
    </div>
  );
}
