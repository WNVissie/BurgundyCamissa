import React, { useState, useEffect, useCallback } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useAuth } from '../../contexts/AuthContext';
import { rosterAPI, employeesAPI, shiftsAPI, areasAPI } from '../../lib/api';
import api from '../../lib/api';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Calendar as CalendarIcon, 
  Clock, 
  User, 
  CheckCircle, 
  AlertCircle,
  XCircle,
  ChevronLeft,
  ChevronRight,
  RotateCcw
} from 'lucide-react';
import { format, addDays, startOfWeek, endOfWeek, eachDayOfInterval, isSameDay } from 'date-fns';

const ItemTypes = {
  EMPLOYEE: 'employee',
  ROSTER_ENTRY: 'roster_entry'
};

// Draggable Employee Component
function DraggableEmployee({ employee }) {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.EMPLOYEE,
    item: { employee, type: 'employee' },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <div
      ref={drag}
      className={`p-3 bg-white border rounded-lg cursor-move transition-all hover:shadow-md ${
        isDragging ? 'opacity-50 scale-95' : 'opacity-100'
      }`}
    >
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-white text-xs font-medium">
            {employee.name.charAt(0)}{employee.surname.charAt(0)}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {employee.name} {employee.surname}
          </p>
          <p className="text-xs text-gray-500">{employee.employee_id}</p>
        </div>
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
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
    </div>
  );
}

// Draggable Roster Entry Component
function DraggableRosterEntry({ rosterEntry, employee, shift, onApproval }) {
  const { isAdmin, isManager } = useAuth();
  
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.ROSTER_ENTRY,
    item: { rosterEntry, type: 'roster_entry' },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-3 w-3" />;
      case 'pending': return <AlertCircle className="h-3 w-3" />;
      case 'rejected': return <XCircle className="h-3 w-3" />;
      default: return <AlertCircle className="h-3 w-3" />;
    }
  };

  return (
    <div
      ref={drag}
      className={`p-2 rounded-md border text-xs cursor-move transition-all hover:shadow-sm ${
        getStatusColor(rosterEntry.status)
      } ${isDragging ? 'opacity-50 scale-95' : 'opacity-100'}`}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium truncate">
          {employee?.name} {employee?.surname}
        </span>
        {getStatusIcon(rosterEntry.status)}
      </div>
      
      <div className="flex items-center text-xs opacity-75 mb-1">
        <Clock className="h-3 w-3 mr-1" />
        {shift?.start_time} - {shift?.end_time}
      </div>
      
      <div className="text-xs opacity-75 mb-2 truncate">
        {shift?.name}
      </div>
      
      {(isAdmin() || isManager()) && rosterEntry.status === 'pending' && (
        <div className="flex space-x-1">
      <Button
            size="sm"
            variant="outline"
            className="h-5 px-1 text-xs"
            onClick={(e) => {
              e.stopPropagation();
        onApproval(rosterEntry.id, 'approve');
            }}
          >
            ✓
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="h-5 px-1 text-xs"
            onClick={(e) => {
              e.stopPropagation();
        onApproval(rosterEntry.id, 'reject');
            }}
          >
            ✗
          </Button>
        </div>
      )}
    </div>
  );
}

// Drop Zone for Calendar Days (table cell version)
function CalendarDropZone({ day, children, onDrop, isToday }) {
  const [{ isOver, canDrop }, drop] = useDrop(() => ({
    accept: [ItemTypes.EMPLOYEE, ItemTypes.ROSTER_ENTRY],
    drop: (item) => onDrop(item, day),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  return (
    <td
      ref={drop}
      className={`align-top p-2 min-w-[160px] border ${
        isToday ? 'bg-blue-50' : 'bg-white'
      } ${
        isOver && canDrop ? 'ring-2 ring-green-500' : ''
      } ${
        isOver && !canDrop ? 'ring-2 ring-red-500' : ''
      }`}
    >
      {children}
    </td>
  );
}

// Shift Selection Modal
function ShiftSelectionModal({ isOpen, onClose, onSelect, shifts, employee, areas }) {
  const [swapArea, setSwapArea] = useState(false);
  const [selectedArea, setSelectedArea] = useState(employee ? employee.area_of_responsibility_id : "");

  if (!isOpen || !employee) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">
          Select Shift for {employee?.name} {employee?.surname}
        </h3>
        <div className="mb-4">
          <label>
            <input
              type="checkbox"
              checked={swapArea}
              onChange={e => setSwapArea(e.target.checked)}
            />
            Swap Area
          </label>
          {swapArea && (
            <select
              value={selectedArea}
              onChange={e => setSelectedArea(e.target.value)}
              className="ml-2 border rounded p-1"
            >
              <option value="">Select an area...</option>
              {areas.map(area => (
                <option key={area.id} value={area.id}>
                  {area.name}
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {shifts.map((shift) => (
            <button
              key={shift.id}
              onClick={() => onSelect(shift, swapArea ? selectedArea : employee.area_of_responsibility_id)}
              className="w-full text-left p-3 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              {shift.name} ({shift.start_time} - {shift.end_time})
            </button>
          ))}
        </div>
        <div className="flex justify-end mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

// Main Drag and Drop Roster Component
export function DragDropRoster() {
  const { isAdmin, isManager } = useAuth();
  const [roster, setRoster] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [showShiftModal, setShowShiftModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);

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
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch roster data');
    } finally {
      setLoading(false);
    }
  }, [currentWeek]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDrop = async (item, targetDate) => {
    if (!isAdmin() && !isManager()) return;

    if (item.type === 'employee') {
      // Show shift selection modal
      setSelectedEmployee(item.employee);
      setSelectedDate(targetDate);
      setShowShiftModal(true);
    } else if (item.type === 'roster_entry') {
      // Move existing roster entry
      try {
        await rosterAPI.update(item.rosterEntry.id, {
          date: format(targetDate, 'yyyy-MM-dd')
        });
        fetchData();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to move shift');
      }
    }
  };

  const handleShiftSelect = async (shift, areaId) => {
    try {
      const rosterData = {
        employee_id: selectedEmployee.id,
        shift_id: shift.id,
        date: format(selectedDate, 'yyyy-MM-dd'),
        status: 'pending',
        hours: shift.hours,
        area_of_responsibility_id: areaId
      };
      
      await rosterAPI.create(rosterData);
      setShowShiftModal(false);
      setSelectedEmployee(null);
      setSelectedDate(null);
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

  // helpers in table layout are inlined per cell

  const getShift = (shiftId) => {
    return shifts.find(s => s.id === shiftId);
  };

  const getArea = (areaId) => {
    return areas.find(a => a.id === areaId);
  };


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

  // Build roster map by employee and date
  const rosterByEmpDate = new Map();
  roster.forEach((entry) => {
    const key = `${entry.employee_id}-${entry.date}`;
    rosterByEmpDate.set(key, entry);
  });

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Interactive Shift Roster</h1>
            <p className="text-gray-600 mt-1">Drag and drop to schedule shifts</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => navigateWeek(-1)}>
              <ChevronLeft className="h-4 w-4 mr-2" /> Prev
            </Button>
            <div className="text-center">
              <h2 className="text-lg font-semibold">
                {format(weekDays[0], 'MMM d')} - {format(weekDays[6], 'MMM d, yyyy')}
              </h2>
              <p className="text-sm text-gray-500">Drag & Drop Scheduling</p>
            </div>
            <Button variant="outline" onClick={() => navigateWeek(1)}>
              Next <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
            <Button onClick={() => fetchData()} variant="outline">
              <RotateCcw className="h-4 w-4 mr-2" /> Refresh
            </Button>
            <Button
              variant="outline"
              onClick={async () => {
                try {
                  const params = {
                    start_date: format(weekDays[0], 'yyyy-MM-dd'),
                    end_date: format(weekDays[6], 'yyyy-MM-dd')
                  };
                  const res = await api.get('/export/roster/grid/excel', { params, responseType: 'blob' });
                  const url = window.URL.createObjectURL(new Blob([res.data]));
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `roster_grid_${format(new Date(), 'yyyyMMdd')}.xlsx`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                } catch {
                  setError('Failed to export roster grid to Excel');
                }
              }}
            >
              Export Grid
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Roster Grid: Employees x Week Days */}
        <div className="overflow-auto border rounded-md">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="p-2 text-left w-64">Employee</th>
                {weekDays.map((day, idx) => (
                  <th key={idx} className="p-2 text-center min-w-[160px]">
                    <div className="font-medium">{format(day, 'EEE')}</div>
                    <div className="text-xs text-gray-500">{format(day, 'MMM d')}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr key={emp.id} className="border-t">
                  {/* Draggable employee handle */}
                  <td className="p-2 align-top">
                    <DraggableEmployee employee={emp} />
                  </td>
                  {weekDays.map((day, idx) => {
                    const key = `${emp.id}-${format(day, 'yyyy-MM-dd')}`;
                    const entry = rosterByEmpDate.get(key);
                    const isToday = isSameDay(day, new Date());
                    const shift = entry ? getShift(entry.shift_id) : null;
                    const area = entry?.area_of_responsibility_id ? getArea(entry.area_of_responsibility_id) : null;
                    const isDifferentArea = area && area.id !== emp.area_of_responsibility_id;
                    return (
                      <CalendarDropZone
                        key={idx}
                        day={day}
                        onDrop={(item, droppedDay) => handleDrop(item, droppedDay)}
                        isToday={isToday}
                      >
                        {entry ? (
                          <div
                            className="p-2 rounded-md border text-xs relative"
                            style={{ backgroundColor: (shift?.color || '#e5e7eb') + '20', borderColor: shift?.color || '#e5e7eb' }}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium truncate">{shift?.name}</span>
                              <span className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded ${
                                entry.status === 'approved' ? 'bg-green-100 text-green-800' : entry.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {entry.status === 'approved' ? <CheckCircle className="h-3 w-3 text-green-600" /> : entry.status === 'rejected' ? <XCircle className="h-3 w-3 text-red-600" /> : <AlertCircle className="h-3 w-3 text-yellow-600" />}
                                {entry.status}
                              </span>
                            </div>
                            <div className="flex items-center text-xs opacity-75 mb-1">
                              <Clock className="h-3 w-3 mr-1" />
                              {shift?.start_time} - {shift?.end_time} • {entry.hours}h
                            </div>
                            {area && (
                              <div className={`text-xs mt-1 p-1 rounded ${
                                isDifferentArea ? 'bg-red-100 text-red-800 font-bold' : 'opacity-75'
                              }`}>
                                Area: {area.name}
                              </div>
                            )}
                            {(isAdmin() || isManager()) && entry.status === 'pending' && (
                              <div className="flex gap-1">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-6 px-2 text-xs border-green-600 text-green-700 hover:bg-green-50"
                                  onClick={() => handleApproval(entry.id, 'approve')}
                                >
                                  ✓
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-6 px-2 text-xs border-red-600 text-red-700 hover:bg-red-50"
                                  onClick={() => handleApproval(entry.id, 'reject')}
                                >
                                  ✗
                                </Button>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-center text-gray-400 py-8">
                            <CalendarIcon className="h-6 w-6 mx-auto mb-1 opacity-50" />
                            <p className="text-[11px]">Drop here</p>
                          </div>
                        )}
                      </CalendarDropZone>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Shift Selection Modal */}
        <ShiftSelectionModal
          isOpen={showShiftModal}
          onClose={() => {
            setShowShiftModal(false);
            setSelectedEmployee(null);
            setSelectedDate(null);
          }}
          onSelect={handleShiftSelect}
          shifts={shifts}
          employee={selectedEmployee}
          areas={areas}
        />
      </div>
    </DndProvider>
  );
}

