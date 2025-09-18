import React, { useState, useEffect, useMemo } from 'react';
import { leaveAPI } from '../lib/api';
import { Input } from './ui/input';
import { Button } from './ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Badge } from './ui/badge';
import { X, FileText, Search, FileType } from 'lucide-react';
import { format, parseISO } from 'date-fns';

export function LeaveTable() {
  console.log('LeaveTable component rendering...');
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Table filters
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    leave_type: '',
    start_date: '',
    end_date: ''
  });
  
  // Active status view for quick filtering
  const [activeStatusView, setActiveStatusView] = useState('all');
  
  // Remove showFilters state - filters will always be visible

  // Load leave requests data
  useEffect(() => {
    const loadLeaveRequests = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await leaveAPI.getAll();
        console.log('Leave API response:', response.data);
        
        // Handle different response structures
        let leaveData = [];
        if (response.data) {
          if (Array.isArray(response.data.leave_requests)) {
            leaveData = response.data.leave_requests;
          } else if (Array.isArray(response.data)) {
            leaveData = response.data;
          }
        }
        
        setLeaveRequests(leaveData);
      } catch (err) {
        console.error('Error loading leave requests:', err);
        setError('Failed to load leave requests');
        setLeaveRequests([]);
      } finally {
        setLoading(false);
      }
    };

    loadLeaveRequests();
  }, []);

  // Apply filters to the leave requests
  const filteredLeaveRequests = useMemo(() => {
    if (!Array.isArray(leaveRequests)) return [];
    
    return leaveRequests.filter(request => {
      // Status view filter (primary filter)
      const matchesStatusView = activeStatusView === 'all' || request.status === activeStatusView;
      
      const matchesSearch = !filters.search || 
        (request.employee?.name?.toLowerCase().includes(filters.search.toLowerCase()) ||
         request.employee?.surname?.toLowerCase().includes(filters.search.toLowerCase()) ||
         request.reason?.toLowerCase().includes(filters.search.toLowerCase()));
      
      const matchesStatus = !filters.status || request.status === filters.status;
      
      const matchesLeaveType = !filters.leave_type || request.leave_type === filters.leave_type;
      
      const matchesStartDate = !filters.start_date || 
        new Date(request.start_date) >= new Date(filters.start_date);
      
      const matchesEndDate = !filters.end_date || 
        new Date(request.end_date) <= new Date(filters.end_date);
      
      return matchesStatusView && matchesSearch && matchesStatus && matchesLeaveType && matchesStartDate && matchesEndDate;
    });
  }, [leaveRequests, filters, activeStatusView]);

  const clearFilters = () => {
    setFilters({
      search: '',
      status: '',
      leave_type: '',
      start_date: '',
      end_date: ''
    });
    setActiveStatusView('all'); // Reset status view to 'all'
  };

  // Export function
  const exportToPDF = (data, filename, title) => {
    if (!data || data.length === 0) {
      alert('No data to export');
      return;
    }

    // Format data for export
    const exportData = data.map(leave => ({
      'Employee': leave.employee ? `${leave.employee.name} ${leave.employee.surname}` : (leave.employee_name || leave.name || ''),
      'Leave Type': leave.leave_type || '',
      'Start Date': leave.start_date || '',
      'End Date': leave.end_date || '',
      'Days': leave.days || leave.total_days || 0,
      'Status': leave.status || '',
      'Reason': leave.reason || '',
      'Applied Date': leave.created_at ? new Date(leave.created_at).toLocaleDateString() : 
                     (leave.applied_date ? new Date(leave.applied_date).toLocaleDateString() : ''),
      'Approved By': leave.approver ? `${leave.approver.name} ${leave.approver.surname}` : 
                     (leave.approved_by_name || '')
    }));

    const headers = Object.keys(exportData[0]);
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { color: #333; margin-bottom: 20px; }
          table { border-collapse: collapse; width: 100%; margin-top: 10px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f2f2f2; font-weight: bold; }
          tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
      </head>
      <body>
        <h1>${title}</h1>
        <table>
          <thead>
            <tr>
              ${headers.map(header => `<th>${header}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${exportData.map(row => 
              `<tr>${headers.map(header => `<td>${row[header] || ''}</td>`).join('')}</tr>`
            ).join('')}
          </tbody>
        </table>
      </body>
      </html>
    `;

    const printWindow = window.open('', '_blank');
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    printWindow.print();
  };

  const getStatusBadgeVariant = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved':
      case 'authorised':
        return 'default';
      case 'pending':
        return 'secondary';
      case 'rejected':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'bg-blue-500 text-white';
      case 'authorised':
        return 'bg-green-500 text-white';
      case 'pending':
        return 'bg-yellow-500 text-white';
      case 'rejected':
        return 'bg-red-500 text-white';
      default:
        return '';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading leave requests...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600">{error}</p>
        <Button 
          onClick={() => window.location.reload()} 
          className="mt-4"
          variant="outline"
        >
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          <h3 className="text-lg font-semibold">
            Leave Requests ({filteredLeaveRequests.length})
          </h3>
        </div>
        {filteredLeaveRequests.length > 0 && (
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportToPDF(filteredLeaveRequests, 'leave-requests', 'Leave Requests')}
            >
              <FileType className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>
        )}
      </div>

      {/* Status View Tabs */}
      <div className="flex flex-wrap gap-2 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
        <div className="w-full mb-2">
          <h4 className="text-sm font-semibold text-blue-800">Filter by Status:</h4>
        </div>
        {console.log('Rendering status tabs, activeStatusView:', activeStatusView)}
        <button
          onClick={() => setActiveStatusView('all')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeStatusView === 'all'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          All ({leaveRequests.length})
        </button>
        <button
          onClick={() => setActiveStatusView('pending')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeStatusView === 'pending'
              ? 'bg-yellow-600 text-white shadow-sm'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          Pending ({leaveRequests.filter(r => r.status === 'pending').length})
        </button>
        <button
          onClick={() => setActiveStatusView('approved')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeStatusView === 'approved'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          Approved ({leaveRequests.filter(r => r.status === 'approved').length})
        </button>
        <button
          onClick={() => setActiveStatusView('authorised')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeStatusView === 'authorised'
              ? 'bg-green-600 text-white shadow-sm'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          Authorised ({leaveRequests.filter(r => r.status === 'authorised').length})
        </button>
        <button
          onClick={() => setActiveStatusView('rejected')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeStatusView === 'rejected'
              ? 'bg-red-600 text-white shadow-sm'
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
        >
          Rejected ({leaveRequests.filter(r => r.status === 'rejected').length})
        </button>
      </div>

      {/* Filters - Always visible */}
      <div className="border rounded-lg p-4 bg-gray-50 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Search</label>
              <Input
                placeholder="Search by employee or reason..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <option value="">All statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="authorised">Authorised</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Leave Type</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.leave_type}
                onChange={(e) => setFilters({ ...filters, leave_type: e.target.value })}
              >
                <option value="">All types</option>
                <option value="Unpaid">Unpaid</option>
                <option value="Paid">Paid</option>
                <option value="Sick">Sick</option>
                <option value="Maternity leave">Maternity leave</option>
                <option value="Special leave">Special leave</option>
                <option value="Family Responsibility leave">Family Responsibility leave</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">From Date</label>
              <Input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">To Date</label>
              <Input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
              />
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={clearFilters} size="sm">
              <X className="h-4 w-4 mr-1" />
              Clear Filters
            </Button>
          </div>
        </div>

      {/* Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee</TableHead>
              <TableHead>Leave Type</TableHead>
              <TableHead>Period</TableHead>
              <TableHead>Days</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Applied Date</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredLeaveRequests.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                  No leave requests found
                </TableCell>
              </TableRow>
            ) : (
              filteredLeaveRequests.map((request) => (
                <TableRow key={request.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">
                        {request.employee?.name || 'Unknown'} {request.employee?.surname || ''}
                      </div>
                      <div className="text-sm text-gray-500">
                        {request.employee?.employee_id || 'N/A'}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {request.leave_type || 'N/A'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div>{format(parseISO(request.start_date), 'MMM d, yyyy')}</div>
                      <div className="text-gray-500">to</div>
                      <div>{format(parseISO(request.end_date), 'MMM d, yyyy')}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="font-medium">
                      {request.days || 
                       Math.ceil((new Date(request.end_date) - new Date(request.start_date)) / (1000 * 60 * 60 * 24)) + 1}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={getStatusBadgeVariant(request.status)}
                      className={getStatusBadgeClass(request.status)}
                    >
                      {request.status || 'pending'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-xs truncate" title={request.reason}>
                      {request.reason || 'No reason provided'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-gray-500">
                      {request.created_at ? format(parseISO(request.created_at), 'MMM d, yyyy') : 'N/A'}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Summary */}
      {filteredLeaveRequests.length > 0 && (
        <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <span className="font-medium">Total: </span>
              {filteredLeaveRequests.length}
            </div>
            <div>
              <span className="font-medium">Pending: </span>
              {filteredLeaveRequests.filter(r => r.status === 'pending').length}
            </div>
            <div>
              <span className="font-medium">Approved: </span>
              {filteredLeaveRequests.filter(r => r.status === 'approved' || r.status === 'authorised').length}
            </div>
            <div>
              <span className="font-medium">Rejected: </span>
              {filteredLeaveRequests.filter(r => r.status === 'rejected').length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
