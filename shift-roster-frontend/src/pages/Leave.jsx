import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { leaveAPI } from '../lib/api';
import { compressImage, validateFile, formatFileSize } from '../lib/imageUtils';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { FileViewer } from '../components/FileViewer';
import { LeaveTable } from '../components/LeaveTable';
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
  Plus,
  Check,
  X,
  Download,
  Plane,
  AlertCircle,
  Trash2,
  Paperclip,
  Upload,
  Filter,
  FileDown,
  FileText,
  Search
} from 'lucide-react';
import { format, parseISO } from 'date-fns';

export function Leave() {
  const { user } = useAuth();
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [form, setForm] = useState({
    leave_type: 'Unpaid',
    start_date: '',
    end_date: '',
    reason: '',
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState('');
  
  // Filters state - TEMPORARILY DISABLED
  // const [filters, setFilters] = useState({
  //   employee: '',
  //   status: '',
  //   leave_type: '',
  //   start_date: '',
  //   end_date: '',
  //   search: ''
  // });
  // const [employees, setEmployees] = useState([]);
  // const [showFilters, setShowFilters] = useState(false);
  
  // File viewer state
  const [fileViewerOpen, setFileViewerOpen] = useState(false);
  const [viewingFile, setViewingFile] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [actionType, setActionType] = useState(''); // 'approve', 'reject', 'authorise'
  const [comment, setComment] = useState('');
  const [selectedLeaveId, setSelectedLeaveId] = useState(null);
  
  // Status view state
  const [activeStatusView, setActiveStatusView] = useState('All');

  const isManager = useMemo(() => user?.role?.name === 'Admin' || user?.role?.name === 'Manager', [user]);

  // Filter leave requests based on active status view
  const filteredLeaveRequests = useMemo(() => {
    if (activeStatusView === 'All') return leaveRequests;
    return leaveRequests.filter(req => {
      switch (activeStatusView) {
        case 'Pending':
          return req.status === 'pending';
        case 'Approved':
          return req.status === 'approved';
        case 'Authorised':
          return req.status === 'authorised';
        case 'Rejected':
          return req.status === 'rejected';
        default:
          return true;
      }
    });
  }, [leaveRequests, activeStatusView]);

  const fetchLeaveRequests = async (filterParams = {}) => {
    try {
      setLoading(true);
      const res = await leaveAPI.getAll(filterParams);
      console.log('Leave requests API response:', res.data);
      
      // Ensure we always set an array
      let leaveData = [];
      if (res.data) {
        if (Array.isArray(res.data.leave_requests)) {
          leaveData = res.data.leave_requests;
        } else if (Array.isArray(res.data)) {
          leaveData = res.data;
        }
      }
      
      setLeaveRequests(leaveData);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch leave requests');
      setLeaveRequests([]); // Ensure it's always an array
    } finally {
      setLoading(false);
    }
  };

  // TEMPORARILY DISABLED - Filter functions
  // const applyFilters = () => {
  //   // Convert filters to query params, excluding empty values
  //   const queryParams = Object.entries(filters).reduce((acc, [key, value]) => {
  //     if (value && value !== '') {
  //       acc[key] = value;
  //     }
  //     return acc;
  //   }, {});
  //   
  //   fetchLeaveRequests(queryParams);
  // };

  // const clearFilters = () => {
  //   setFilters({
  //     employee: '',
  //     status: '',
  //     leave_type: '',
  //     start_date: '',
  //     end_date: '',
  //     search: ''
  //   });
  //   // Fetch with no filters
  //   fetchLeaveRequests();
  // };

  useEffect(() => {
    fetchLeaveRequests();
    // TEMPORARILY DISABLED - Employee fetching for filters
    // if (isManager) {
    //   fetchEmployees();
    // }
  }, [isManager]);

  // TEMPORARILY DISABLED - fetchEmployees function
  // const fetchEmployees = async () => {
  //   try {
  //     const res = await employeesAPI.getAll();
  //     console.log('Employees API response:', res.data);
  //     
  //     // Handle different response structures
  //     let employeesData = [];
  //     if (res.data) {
  //       if (Array.isArray(res.data.employees)) {
  //         employeesData = res.data.employees;
  //       } else if (Array.isArray(res.data)) {
  //         employeesData = res.data;
  //       }
  //     }
  //     
  //     setEmployees(employeesData);
  //     console.log('Set employees:', employeesData);
  //   } catch (err) {
  //     console.error('Failed to fetch employees:', err);
  //     setEmployees([]); // Ensure it's always an array
  //   }
  // };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFileError('');
    
    try {
      let requestData;
      
      // If there's a file, use FormData
      if (selectedFile) {
        requestData = new FormData();
        requestData.append('leave_type', form.leave_type);
        requestData.append('start_date', form.start_date);
        requestData.append('end_date', form.end_date);
        requestData.append('reason', form.reason);
        requestData.append('attachment', selectedFile);
      } else {
        // Use regular JSON data
        requestData = form;
      }
      
      await leaveAPI.create(requestData);
      setIsDialogOpen(false);
      setForm({ leave_type: 'Unpaid', start_date: '', end_date: '', reason: '' });
      setSelectedFile(null);
      setFileError('');
      fetchLeaveRequests();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit leave request');
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) {
      setSelectedFile(null);
      setFileError('');
      return;
    }

    try {
      // Validate file first
      const validation = validateFile(file, {
        maxSizeKB: 5120, // 5MB for initial validation
        allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      });

      if (!validation.isValid) {
        setFileError(validation.errors.join('. '));
        setSelectedFile(null);
        return;
      }

      let processedFile = file;

      // Compress images to reduce size
      if (file.type.startsWith('image/')) {
        setFileError('Compressing image...');
        try {
          processedFile = await compressImage(file, {
            maxWidth: 1200,
            maxHeight: 1200,
            quality: 0.8,
            maxSizeKB: 1000, // Target 1MB after compression
          });
          
          // Validate compressed file size
          if (processedFile.size > 2 * 1024 * 1024) { // 2MB hard limit
            setFileError(`Compressed image is still too large (${formatFileSize(processedFile.size)}). Please use a smaller image.`);
            setSelectedFile(null);
            return;
          }
        } catch (compressionError) {
          console.error('Image compression failed:', compressionError);
          setFileError('Failed to compress image. Please try a different image.');
          setSelectedFile(null);
          return;
        }
      } else {
        // For non-images, enforce stricter size limit
        if (file.size > 2 * 1024 * 1024) { // 2MB limit for documents
          setFileError(`File size (${formatFileSize(file.size)}) is too large. Maximum allowed: 2MB`);
          setSelectedFile(null);
          return;
        }
      }

      setSelectedFile(processedFile);
      setFileError('');
      
      // Show compression results for images
      if (file.type.startsWith('image/') && processedFile.size !== file.size) {
        const compressionRatio = ((file.size - processedFile.size) / file.size * 100).toFixed(1);
        console.log(`Image compressed: ${formatFileSize(file.size)} → ${formatFileSize(processedFile.size)} (${compressionRatio}% reduction)`);
      }
    } catch (error) {
      console.error('File processing error:', error);
      setFileError('Failed to process file. Please try again.');
      setSelectedFile(null);
    }
  };

  const downloadAttachment = async (requestId, filename) => {
    try {
      const blob = await leaveAPI.downloadAttachmentFile(requestId); // Use new download endpoint
      
      // Create blob URL and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download attachment:', error);
      setError('Failed to download attachment');
    }
  };

  const viewAttachment = (leaveRequest) => {
    setViewingFile({
      leaveId: leaveRequest.id,
      filename: leaveRequest.attachment.filename,
      mimetype: leaveRequest.attachment.mimetype
    });
    setFileViewerOpen(true);
  };

  const closeFileViewer = () => {
    setFileViewerOpen(false);
    setViewingFile(null);
  };

/*  was used for confirm/reject leave without comment (option to use only if no comments is required and the function need to be changed)
const handleAction = async (id, action) => {
    if (!window.confirm(`Are you sure you want to ${action} this request?`)) return;
    try {
      await leaveAPI.action(id, { action });
      fetchLeaveRequests();
    } catch (err) {
      setError(err.response?.data?.error || `Failed to ${action} leave request`);
    }
  };*/

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this request?')) return;
    try {
      await leaveAPI.delete(id);
      fetchLeaveRequests();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete leave request');
    }
  }

  const handleActionClick = (leaveId, type) => {
    setSelectedLeaveId(leaveId);
    setActionType(type);
    setShowModal(true);
  };

  const handleConfirmAction = async () => {
    try {
      const payload = {
        action: actionType === 'authorise' ? 'authorise' : actionType,
        action_comment: comment
      };
      
      // Use appropriate endpoint based on action type
      if (actionType === 'authorise') {
        await leaveAPI.authorise(selectedLeaveId, payload);
      } else {
        await leaveAPI.approve(selectedLeaveId, payload);
      }
      
      setShowModal(false);
      setComment('');
      fetchLeaveRequests();
    } catch (err) {
      setError(err.response?.data?.error || `Failed to ${actionType} leave request`);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'authorised':
        return <Badge variant="success">Authorised</Badge>;
      case 'approved':
        return <Badge className="bg-blue-100 text-blue-800">Approved</Badge>;
      case 'rejected':
        return <Badge variant="destructive">Rejected</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
    }
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
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <Plane className="h-5 w-5 mr-2" />
                Leave Management
              </CardTitle>
              <CardDescription>
                Request time off and view your leave history. {isManager && "Managers can approve or reject requests."}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {/* TEMPORARILY DISABLED - Filter button causing issues */}
              {/*
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2"
              >
                <Filter className="h-4 w-4" />
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </Button>
              */}
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Request Leave
                  </Button>
                </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>New Leave Request</DialogTitle>
                  <DialogDescription>
                    Fill out the form to request time off.  This document is to be ompleted for any workday that has not been/will be attended by a staff member
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="leave-type">Leave Type</Label>
                    <select
                      id="leave-type"
                      value={form.leave_type}
                      onChange={(e) => setForm({ ...form, leave_type: e.target.value })}
                      className="w-full mt-1 p-2 border rounded-md"
                    >
                      <option>Unpaid</option>
                      <option>Paid</option>
                      <option>Sick</option>
                      <option>Maternity leave</option>
                      <option>Special leave</option>
                      <option>Family Responsibility leave</option>
                      <option>Other</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="start-date">Start Date</Label>
                      <Input
                        id="start-date"
                        type="date"
                        value={form.start_date}
                        onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="end-date">End Date</Label>
                      <Input
                        id="end-date"
                        type="date"
                        value={form.end_date}
                        onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="reason">Reason</Label>
                    <Textarea
                      id="reason"
                      value={form.reason}
                      onChange={(e) => setForm({ ...form, reason: e.target.value })}
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="attachment">Supporting Document (Optional)</Label>
                    <div className="mt-2">
                      <Input
                        id="attachment"
                        type="file"
                        onChange={handleFileChange}
                        accept=".png,.jpg,.jpeg,.gif,.pdf,.doc,.docx"
                        className="cursor-pointer"
                      />
                      <p className="text-sm text-gray-500 mt-1">
                        Accepted files: Images (PNG, JPG, GIF), PDF, Word documents. Images will be automatically compressed. Max size: 2MB
                      </p>
                      {selectedFile && (
                        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
                          <div className="flex items-center text-sm text-green-700">
                            <Paperclip className="h-4 w-4 mr-1" />
                            {selectedFile.name} ({formatFileSize(selectedFile.size)})
                            {selectedFile.type.startsWith('image/') && (
                              <span className="ml-2 text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                                Compressed
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                      {fileError && (
                        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                          <div className="flex items-center text-sm text-red-700">
                            {fileError.includes('Compressing') ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-500 mr-2"></div>
                                {fileError}
                              </>
                            ) : (
                              <>
                                <AlertCircle className="h-4 w-4 mr-1" />
                                {fileError}
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <DialogFooter>
                    <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit">Submit Request</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
            </div>
          </div>
        </CardHeader>
        
        {/* TEMPORARILY DISABLED - Filters Section causing errors */}
        {/*
        {showFilters && (
          <CardContent className="border-b">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              {isManager && (
                <div>
                  <Label htmlFor="filter-employee">Employee</Label>
                  <Select
                    value={filters.employee}
                    onValueChange={(value) => setFilters({ ...filters, employee: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All employees" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All employees</SelectItem>
                      {Array.isArray(employees) && employees.map((emp) => (
                        <SelectItem key={emp.id} value={emp.id.toString()}>
                          {emp.name || emp.first_name || 'Unknown'} {emp.surname || emp.last_name || ''}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              
              <div>
                <Label htmlFor="filter-status">Status</Label>
                <Select
                  value={filters.status}
                  onValueChange={(value) => setFilters({ ...filters, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All statuses" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All statuses</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="authorised">Authorised</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="filter-leave-type">Leave Type</Label>
                <Select
                  value={filters.leave_type}
                  onValueChange={(value) => setFilters({ ...filters, leave_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All types" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All types</SelectItem>
                    <SelectItem value="Unpaid">Unpaid</SelectItem>
                    <SelectItem value="Paid">Paid</SelectItem>
                    <SelectItem value="Sick">Sick</SelectItem>
                    <SelectItem value="Maternity leave">Maternity leave</SelectItem>
                    <SelectItem value="Special leave">Special leave</SelectItem>
                    <SelectItem value="Family Responsibility leave">Family Responsibility leave</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="filter-search">Search</Label>
                <Input
                  id="filter-search"
                  placeholder="Search by reason..."
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <Label htmlFor="filter-start-date">Start Date</Label>
                <Input
                  id="filter-start-date"
                  type="date"
                  value={filters.start_date}
                  onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="filter-end-date">End Date</Label>
                <Input
                  id="filter-end-date"
                  type="date"
                  value={filters.end_date}
                  onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                />
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button onClick={applyFilters} className="flex items-center gap-2">
                <Search className="h-4 w-4" />
                Apply Filters
              </Button>
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </CardContent>
        )}
        */}
        
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Status View Tabs */}
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {['All', 'Pending', 'Approved', 'Authorised', 'Rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => setActiveStatusView(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeStatusView === status
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
          
          <Table>
            <TableHeader>
              <TableRow>
                {isManager && <TableHead>Employee</TableHead>}
                <TableHead>Type</TableHead>
                <TableHead>Dates</TableHead>
                <TableHead>Days</TableHead>
                <TableHead>Days Remaining</TableHead>
                <TableHead>Approved By</TableHead>
                <TableHead>Authorised By</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Attachment</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Comments</TableHead>
                <TableHead>Approve</TableHead>
                <TableHead>Authorise</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Array.isArray(filteredLeaveRequests) && filteredLeaveRequests.map((req) => (
                <TableRow key={req.id}>
                  {isManager && <TableCell>{req.employee?.name || 'Unknown'} {req.employee?.surname || ''}</TableCell>}
                  <TableCell>{req.leave_type}</TableCell>
                  <TableCell>
                    {format(parseISO(req.start_date), 'MMM d, yyyy')} - {format(parseISO(req.end_date), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell>{Number(req.days).toFixed(2)}</TableCell>
                  <TableCell>{req.no_of_leave_days_remaining ? Number(req.no_of_leave_days_remaining).toFixed(2) : '0.00'}</TableCell>
                  <TableCell>
                    {req.approver ? `${req.approver.name} ${req.approver.surname}` : '-'}
                  </TableCell>
                  <TableCell>{req.authorised_by_name || '-'}</TableCell>
                  <TableCell className="max-w-xs truncate">{req.reason}</TableCell>
                  <TableCell>
                    {req.has_attachment ? (
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => viewAttachment(req)}
                          className="text-blue-600 hover:text-blue-700"
                          title={`View ${req.attachment.filename}`}
                        >
                          <span className="text-xs">
                            {req.attachment.filename.length > 12 
                              ? `${req.attachment.filename.substring(0, 12)}...` 
                              : req.attachment.filename}
                          </span>
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => downloadAttachment(req.id, req.attachment.filename)}
                          className="text-gray-600 hover:text-gray-700"
                          title="Download file"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">No attachment</span>
                    )}
                  </TableCell>
                  <TableCell>{getStatusBadge(req.status)}</TableCell>
                  <TableCell className="max-w-xs truncate">{req.action_comment || ''}</TableCell>
                  
                  {/* Approve Column */}
                  <TableCell>
                    {isManager && req.status === 'pending' && (
                      <div className="flex space-x-1">
                        <Button variant="ghost" size="sm" className="text-green-600 hover:text-green-700" onClick={() => handleActionClick(req.id, 'approve')}>
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700" onClick={() => handleActionClick(req.id, 'reject')}>
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                    {req.status === 'approved' && (
                      <Badge className="bg-green-100 text-green-800">✓ Approved</Badge>
                    )}
                    {req.status === 'rejected' && (
                      <Badge variant="destructive">✗ Rejected</Badge>
                    )}
                    {!isManager && req.status === 'pending' && (
                      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700" onClick={() => handleDelete(req.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                  
                  {/* Authorise Column */}
                  <TableCell>
                    {isManager && req.status === 'approved' && (
                      <div className="flex space-x-1">
                        <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700" onClick={() => handleActionClick(req.id, 'authorise')}>
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700" onClick={() => handleActionClick(req.id, 'reject')}>
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                    {req.status === 'authorised' && (
                      <Badge variant="success">✓ Authorised</Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      {showModal && (
        <Dialog open={showModal} onOpenChange={setShowModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {actionType === 'approve' && 'Approve Leave Request'}
                {actionType === 'authorise' && 'Authorise Leave Request'}
                {actionType === 'reject' && 'Reject Leave Request'}
              </DialogTitle>
              <DialogDescription>
                {actionType === 'approve' && 'Supervisor approval - first stage of the leave process.'}
                {actionType === 'authorise' && 'Final authorization - leave days will be deducted from employee allowance.'}
                {actionType === 'reject' && 'Reject this leave request with a comment.'}
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <Textarea
                value={comment}
                onChange={e => setComment(e.target.value)}
                placeholder="Add a comment (optional)"
                rows={4}
                style={{ width: '100%' }}
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleConfirmAction}>
                Confirm
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      
      {/* File Viewer */}
      {viewingFile && (
        <FileViewer
          isOpen={fileViewerOpen}
          onClose={closeFileViewer}
          leaveId={viewingFile.leaveId}
          filename={viewingFile.filename}
          mimetype={viewingFile.mimetype}
        />
      )}
    </div>
  );
}
