import React, { useState, useCallback } from 'react';
import { DragDropRoster } from '../components/roster/DragDropRoster';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Calendar as CalendarIcon, 
  Grip,
  List
} from 'lucide-react';

// Original static roster view (keeping for comparison)
import { useAuth } from '../contexts/AuthContext';
import api, { rosterAPI, employeesAPI, shiftsAPI, areasAPI } from '../lib/api';
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
import { Calendar } from '../components/ui/calendar';
import { 
  Plus, 
  Clock, 
  User, 
  CheckCircle, 
  AlertCircle,
  XCircle,
  Filter,
  ChevronLeft,
  ChevronRight,
  Mail,
  MessageSquare
} from 'lucide-react';
import { format, addDays, startOfWeek, endOfWeek, eachDayOfInterval, isSameDay, parseISO } from 'date-fns';

function StaticRosterView() {
  const { isAdmin, isManager, isEmployee, user } = useAuth();
  const [roster, setRoster] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [areas, setAreas] = useState([]);
  //const [leave, setLeave] = useState([]);
  //const [timesheets, setTimesheets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [selectedShift, setSelectedShift] = useState('');
  const [selectedArea, setSelectedArea] = useState('');
  const [selectedRosterDate, setSelectedRosterDate] = useState(new Date());
  const [selectedShifts, setSelectedShifts] = useState(new Set());

  const handleSelectionChange = (shiftId) => {
    setSelectedShifts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(shiftId)) {
        newSet.delete(shiftId);
      } else {
        newSet.add(shiftId);
      }
      return newSet;
    });
  };

  const selectEntireDay = (date) => {
    const dayRoster = getRosterForDate(date);
    const dayShiftIds = dayRoster.map(r => r.id);
    
    setSelectedShifts(prev => {
      const newSet = new Set(prev);
      const allSelected = dayShiftIds.every(id => newSet.has(id));
      
      if (allSelected) {
        // Deselect all shifts for this day
        dayShiftIds.forEach(id => newSet.delete(id));
      } else {
        // Select all shifts for this day
        dayShiftIds.forEach(id => newSet.add(id));
      }
      return newSet;
    });
  };

  const selectEntireWeek = () => {
    const allWeekShiftIds = roster.map(r => r.id);
    
    setSelectedShifts(prev => {
      const newSet = new Set(prev);
      const allSelected = allWeekShiftIds.every(id => newSet.has(id));
      
      if (allSelected) {
        // Deselect entire week
        return new Set();
      } else {
        // Select entire week
        return new Set(allWeekShiftIds);
      }
    });
  };

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const startDate = startOfWeek(currentWeek, { weekStartsOn: 1 });
      const endDate = endOfWeek(currentWeek, { weekStartsOn: 1 });

      const [rosterRes, employeesRes, shiftsRes, areasRes] = await Promise.all([
        rosterAPI.getAll({
          start_date: format(startDate, 'yyyy-MM-dd'),
          end_date: format(endDate, 'yyyy-MM-dd')
        }),
        employeesAPI.getAll(),
        shiftsAPI.getAll(),
        areasAPI.getAll()
      ]);
      
      setRoster(rosterRes.data.roster || []);
      setEmployees(employeesRes.data.employees || []);
      setShifts(shiftsRes.data.shifts || []);
      setAreas(areasRes.data.areas || []);
      //setLeave(leaveRes.data.leave || []);
      //setTimesheets(timesheetsRes.data.timesheets || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch roster data');
    } finally {
      setLoading(false);
    }
  }, [currentWeek]);

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateRoster = async () => {
    try {
      const selShift = shifts.find(s => s.id === parseInt(selectedShift));
            const rosterData = {
        employee_id: parseInt(selectedEmployee),
        shift_id: parseInt(selectedShift),
        date: format(selectedRosterDate, 'yyyy-MM-dd'),
        status: 'pending',
        hours: selShift?.hours,
        area_of_responsibility_id: selectedArea === "default" ? null : parseInt(selectedArea)
      };
      
      await rosterAPI.create(rosterData);
      setIsDialogOpen(false);
      setSelectedEmployee('');
      setSelectedShift('');
      setSelectedArea('');
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create roster entry');
    }
  };

  const handleApproval = async (rosterId, action) => {
    try {
      await rosterAPI.approve(rosterId, { action });
      fetchData();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update approval status');
    }
  };

  const getWeekDays = () => {
    const start = startOfWeek(currentWeek, { weekStartsOn: 1 });
    const end = endOfWeek(currentWeek, { weekStartsOn: 1 });
    return eachDayOfInterval({ start, end });
  };

  const getRosterForDate = (date) => {
    if (isAdmin() || isManager()) {
      // Show all shifts for admins/managers
      return roster.filter(r => isSameDay(parseISO(r.date), date));
    }
    // Employees see only their own approved shifts (pending and rejected shifts are hidden)
    return roster.filter(
      r => isSameDay(parseISO(r.date), date) && r.employee_id === user.id && (r.status === 'approved' || r.status === 'accepted')
    );
  };

  const getEmployee = (employeeId) => {
    return employees.find(e => e.id === employeeId);
  };

  const getShift = (shiftId) => shifts.find(s => String(s.id) === String(shiftId));

  const getArea = (areaId) => areas.find(a => a.id === areaId);

  // status helpers moved inline using colored badges

  const navigateWeek = (direction) => {
    setCurrentWeek(prev => addDays(prev, direction * 7));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const weekDays = getWeekDays();

  return (
    <div className="space-y-6">
      {/* Week Navigation */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <Button variant="outline" onClick={() => navigateWeek(-1)}>
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous Week
            </Button>
            
            <div className="text-center">
              <h2 className="text-lg font-semibold">
                {format(weekDays[0], 'MMM d')} - {format(weekDays[6], 'MMM d, yyyy')}
              </h2>
              <p className="text-sm text-gray-500">Traditional View</p>
            </div>
            
            <Button variant="outline" onClick={() => navigateWeek(1)}>
              Next Week
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
          {/* Export controls */}
          <div className="mt-4 flex items-center gap-2 justify-end">
            <Button
              variant="outline"
              onClick={async () => {
                try {
                  const params = {
                    start_date: format(weekDays[0], 'yyyy-MM-dd'),
                    end_date: format(weekDays[6], 'yyyy-MM-dd')
                  };
                  const res = await api.get('/export/roster/excel', { params, responseType: 'blob' });
                  const url = window.URL.createObjectURL(new Blob([res.data]));
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `roster_${format(new Date(), 'yyyyMMdd_HHmmss')}.xlsx`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                } catch {
                  setError('Failed to export roster to Excel');
                }
              }}
            >
              Export Excel
            </Button>
            <Button
              variant="outline"
              onClick={async () => {
                try {
                  const params = {
                    start_date: format(weekDays[0], 'yyyy-MM-dd'),
                    end_date: format(weekDays[6], 'yyyy-MM-dd')
                  };
                  const res = await api.get('/export/roster/pdf', { params, responseType: 'blob' });
                  const url = window.URL.createObjectURL(new Blob([res.data]));
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `roster_${format(new Date(), 'yyyyMMdd_HHmmss')}.pdf`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                } catch {
                  setError('Failed to export roster to PDF');
                }
              }}
            >
              Export PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Add Shift Dialog */}
      {(isAdmin() || isManager()) && (
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Shift
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Schedule New Shift</DialogTitle>
              <DialogDescription>
                Assign an employee to a shift for a specific date.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Employee</label>
                <Select value={selectedEmployee} onValueChange={setSelectedEmployee}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select an employee" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((employee) => (
                      <SelectItem key={employee.id} value={employee.id.toString()}>
                        {employee.name} {employee.surname} - {employee.employee_id}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Temporary Area (Optional)</label>
                <Select value={selectedArea} onValueChange={setSelectedArea}>
                  <SelectTrigger>
                    <SelectValue placeholder="Default to employee's area" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Default Area</SelectItem>
                    {areas.map((area) => (
                      <SelectItem key={area.id} value={area.id.toString()}>
                        {area.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium">Shift</label>
                <Select value={selectedShift} onValueChange={setSelectedShift}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a shift" />
                  </SelectTrigger>
                  <SelectContent>
                    {shifts.map((shift) => (
                      <SelectItem key={shift.id} value={shift.id.toString()}>
                        {shift.name} ({shift.start_time} - {shift.end_time})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium">Date</label>
                <Calendar
                  mode="single"
                  selected={selectedRosterDate}
                  onSelect={setSelectedRosterDate}
                  className="rounded-md border"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateRoster}
                disabled={!selectedEmployee || !selectedShift}
              >
                Schedule
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Weekly Calendar View with colors and scroll container */}
      {(isAdmin() || isManager()) && (
        <div className="grid grid-cols-7 gap-4 max-h-[70vh] overflow-y-auto pr-2">
          {weekDays.map((day, index) => {
            const dayRoster = getRosterForDate(day);
            const isToday = isSameDay(day, new Date());
            
            return (
              <Card key={index} className={`min-h-[300px] ${isToday ? 'ring-2 ring-blue-500' : ''}`}>
                <CardContent className="p-3">
                  <div className="text-center mb-3">
                    <div className="text-sm font-medium">{format(day, 'EEE')}</div>
                    <div className="text-lg font-bold">{format(day, 'd')}</div>
                    {dayRoster.length > 0 && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-1 text-xs h-6 px-2"
                        onClick={() => selectEntireDay(day)}
                      >
                        {dayRoster.every(r => selectedShifts.has(r.id)) ? 'Deselect Day' : 'Select Day'}
                      </Button>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    {dayRoster.map((rosterEntry) => {
                      const employee = getEmployee(rosterEntry.employee_id);
                      const shift = getShift(rosterEntry.shift_id);
                      
                      return (
                        <div
                          key={rosterEntry.id}
                          className={`p-2 rounded-md text-xs`}
                          style={{
                            backgroundColor: (shift?.color || '#e5e7eb') + '20',
                            border: `1px solid ${shift?.color || '#e5e7eb'}`
                          }}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium">
                              {employee?.name} {employee?.surname}
                            </span>
                            <div className="flex flex-col items-end">
                              <span className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded ${
                                rosterEntry.status === 'approved' || rosterEntry.status === 'accepted' ? 'bg-green-100 text-green-800' : rosterEntry.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {rosterEntry.status === 'approved' || rosterEntry.status === 'accepted' ? <CheckCircle className="h-3 w-3 text-green-600" /> : rosterEntry.status === 'rejected' ? <XCircle className="h-3 w-3 text-red-600" /> : <AlertCircle className="h-3 w-3 text-yellow-600" />}
                                {rosterEntry.status === 'accepted' ? 'Approved' : rosterEntry.status}
                              </span>
                              {(rosterEntry.status === 'approved' || rosterEntry.status === 'accepted') && (
                                <span className={`mt-1 inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded ${
                                  rosterEntry.status === 'accepted' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {rosterEntry.status === 'accepted' ? 'Accepted' : 'Not Accepted'}
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center text-xs opacity-75">
                            <Clock className="h-3 w-3 mr-1" />
                            {shift?.start_time} - {shift?.end_time} • {rosterEntry.hours}h
                          </div>
                          
                          <div className="text-xs opacity-75 mt-1">
                            {shift?.name}
                          </div>

                          {rosterEntry.area && (
                            <div className={`text-xs mt-1 p-1 rounded ${
                              rosterEntry.area.id !== employee?.area_of_responsibility_id ? 'bg-red-100 text-red-800 font-bold' : 'opacity-75'
                            }`}>
                              Area: {rosterEntry.area.name}
                            </div>
                          )}
                          
                          <div className="flex items-center justify-between mt-2">
                            <div className="flex items-center space-x-1">
                              <Checkbox
                                id={`select-${rosterEntry.id}`}
                                checked={selectedShifts.has(rosterEntry.id)}
                                onCheckedChange={() => handleSelectionChange(rosterEntry.id)}
                              />
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-6 px-1 text-blue-600 hover:text-blue-700"
                                onClick={() => {
                                  const phone = employee?.contact_no?.replace(/\D/g, '');
                                  const message = `Hi ${employee?.name}, your shift is: ${shift?.name} on ${format(parseISO(rosterEntry.date), 'MMM d, yyyy')} from ${shift?.start_time} to ${shift?.end_time}.`;
                                  window.open(`https://wa.me/${phone}?text=${encodeURIComponent(message)}`, '_blank');
                                }}
                              >
                                <MessageSquare className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-6 px-1 text-red-600 hover:text-red-700"
                                onClick={() => {
                                  const subject = `Shift Details for ${format(parseISO(rosterEntry.date), 'MMM d, yyyy')}`;
                                  const body = `Hi ${employee?.name},\n\nYour shift is:\n- Shift: ${shift?.name}\n- Date: ${format(parseISO(rosterEntry.date), 'MMM d, yyyy')}\n- Time: ${shift?.start_time} - ${shift?.end_time}\n\nThanks`;
                                  window.location.href = `mailto:${employee?.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
                                }}
                              >
                                <Mail className="h-4 w-4" />
                              </Button>
                            </div>

                            {(isAdmin() || isManager()) && rosterEntry.status === 'pending' && (
                              <div className="flex space-x-1">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-6 px-2 text-xs border-green-600 text-green-700 hover:bg-green-50"
                                  onClick={() => handleApproval(rosterEntry.id, 'approve')}
                                >
                                  ✓
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-6 px-2 text-xs border-red-600 text-red-700 hover:bg-red-50"
                                  onClick={() => handleApproval(rosterEntry.id, 'reject')}
                                >
                                  ✗
                                </Button>
                              </div>
                            )}

                            {/* Accept button for employees on their own pending shifts */}
                            {isEmployee() && rosterEntry.employee_id === user.id && rosterEntry.status === 'approved' && !rosterEntry.accepted_at && (
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-6 px-2 text-xs border-green-600 text-green-700 hover:bg-green-50"
                                onClick={async () => {
                                  await rosterAPI.accept(rosterEntry.id);
                                  fetchData();
                                }}
                              >
                                Accept
                              </Button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                    
                    {dayRoster.length === 0 && (
                      <div className="text-center text-gray-400 py-8">
                        <CalendarIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-xs">No shifts scheduled</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Bulk Selection Controls */}
      {(isAdmin() || isManager()) && roster.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium">Bulk Selection:</p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={selectEntireWeek}
                >
                  {roster.every(r => selectedShifts.has(r.id)) ? 'Deselect All Week' : 'Select All Week'}
                </Button>
              </div>
              
              {selectedShifts.size > 0 && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{selectedShifts.size} shift(s) selected</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bulk Actions */}
      {selectedShifts.size > 0 && (
        <Card>
          <CardContent className="p-4 flex items-center justify-between">
            <p className="text-sm font-medium">{selectedShifts.size} shift(s) selected</p>
            <div className="flex space-x-2">
              <Button
                onClick={() => {
                  let message = 'Selected Shifts:\n\n';
                  selectedShifts.forEach(id => {
                    const r = roster.find(r => r.id === id);
                    if (r) {
                      const e = getEmployee(r.employee_id);
                      const s = getShift(r.shift_id);
                      message += `- ${e?.name} ${e?.surname}: ${s?.name} on ${format(parseISO(r.date), 'MMM d, yyyy')} (${s?.start_time}-${s?.end_time})\n`;
                    }
                  });
                  navigator.clipboard.writeText(message);
                  alert('Shift details copied to clipboard!');
                }}
              >
                Copy for WhatsApp
              </Button>
              <Button
                onClick={() => {
                  const selectedRosterEntries = Array.from(selectedShifts).map(id => roster.find(r => r.id === id)).filter(Boolean);
                  const employeesToEmail = [...new Set(selectedRosterEntries.map(r => getEmployee(r.employee_id)))];
                  const emails = employeesToEmail.map(e => e.email).join(',');

                  let body = 'Hi Team,\n\nHere are the selected shift details:\n\n';
                  selectedRosterEntries.forEach(r => {
                    const e = getEmployee(r.employee_id);
                    const s = getShift(r.shift_id);
                    body += `- ${e?.name} ${e?.surname}: ${s?.name} on ${format(parseISO(r.date), 'MMM d, yyyy')} (${s?.start_time}-${s?.end_time})\n`;
                  });

                  window.location.href = `mailto:${emails}?subject=Shift Schedule&body=${encodeURIComponent(body)}`;
                }}
              >
                Email Selected
              </Button>
              <Button variant="outline" onClick={() => setSelectedShifts(new Set())}>Clear Selection</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm font-medium">Approved & Accepted</p>
                <p className="text-2xl font-bold text-green-600">
                  {roster.filter(r => r.status === 'approved' || r.status === 'accepted').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm font-medium">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {roster.filter(r => r.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <XCircle className="h-5 w-5 text-red-600" />
              <div>
                <p className="text-sm font-medium">Rejected</p>
                <p className="text-2xl font-bold text-red-600">
                  {roster.filter(r => r.status === 'rejected').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm font-medium">Total Shifts</p>
                <p className="text-2xl font-bold text-blue-600">
                  {roster.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Employee-specific shift view */}
      {isEmployee() && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-4">My Shifts</h2>
          {roster.filter(r => r.employee_id === user.id && (r.status === 'approved' || r.status === 'accepted')).map(r => {
            const shift = getShift(r.shift_id);
            const area = r.area_of_responsibility_id ? getArea(r.area_of_responsibility_id) : null;
            const isDifferentArea = area && area.id !== user.area_of_responsibility_id;
            return (
              <div key={r.id} className="flex items-center justify-between p-3 rounded-md border mb-2"
                style={{
                  backgroundColor: r.status === 'accepted' ? '#e8f5e9' : '#f3f4f6'
                }}
              >
                <div className="flex-1">
                  <div className="text-sm font-medium">
                    {r.date} - {user.name} {user.surname}
                  </div>
                  <div className="text-xs text-gray-500">
                    {shift?.start_time} - {shift?.end_time} • {r.hours}h
                  </div>
                  <div className="text-xs text-gray-500">
                    {shift?.name}
                  </div>
                  {area && (
                    <div className={`text-xs mt-1 p-1 rounded inline-block ${
                      isDifferentArea ? 'bg-red-100 text-red-800 font-bold' : 'bg-blue-100 text-blue-800'
                    }`}>
                      Area: {area.name}{isDifferentArea ? ' (Temporary Assignment)' : ''}
                    </div>
                  )}
                </div>
                <Button
                  style={{
                    backgroundColor: r.status === 'accepted' ? '#4caf50' : '#e0e0e0',
                    color: r.status === 'accepted' ? '#fff' : '#000',
                    border: 'none'
                  }}
                  onClick={async () => {
                    await rosterAPI.accept(r.id);
                    await fetchData();
                  }}
                  disabled={r.status === 'accepted'}
                >
                  {r.status === 'accepted' ? 'Accepted' : 'Accept'}
                </Button>
              </div>
            );
          })}
          {roster.filter(r => r.employee_id === user.id && r.status !== 'rejected').length === 0 && (
            <div className="text-center text-gray-400 py-8">
              <CalendarIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs">No shifts scheduled</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const TraditionalShiftView = ({ shifts }) => {
  return (
    <div>
      {shifts.map(shift => (
        <div key={shift.id}>
          {/* ...shift details... */}
        </div>
      ))}
    </div>
  );
};

export function Roster() {
  const { isAdmin, isManager } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Shift Roster</h1>
          <p className="text-gray-600 mt-1">Manage employee shift schedules with drag & drop</p>
        </div>
      </div>

      {/* Tabs for different views */}
      {(isAdmin() || isManager()) ? (
        <Tabs defaultValue="drag-drop" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="drag-drop" className="flex items-center">
              <Grip className="h-4 w-4 mr-2" />
              Drag & Drop
            </TabsTrigger>
            <TabsTrigger value="traditional" className="flex items-center">
              <List className="h-4 w-4 mr-2" />
              Traditional View
            </TabsTrigger>
          </TabsList>
          <TabsContent value="drag-drop" className="mt-6">
            <DragDropRoster />
          </TabsContent>
          <TabsContent value="traditional" className="mt-6">
            <StaticRosterView />
          </TabsContent>
        </Tabs>
      ) : (
        // Employees only see traditional view
        <StaticRosterView />
      )}
    </div>
  );
}

