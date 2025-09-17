import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Calendar } from '../ui/calendar';
import { 
  Download, 
  FileText, 
  FileSpreadsheet,
  Calendar as CalendarIcon,
  Users,
  Clock,
  BarChart3,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';

export function ExportModal({ isOpen, onClose, exportType = 'employees' }) {
  const [selectedFormat, setSelectedFormat] = useState('csv');
  const [dateRange, setDateRange] = useState({
    start: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    end: format(endOfMonth(new Date()), 'yyyy-MM-dd')
  });
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState(null);

  const exportOptions = {
    employees: {
      title: 'Export Employees',
      description: 'Export employee data including roles, areas, and skills',
      icon: Users,
      formats: [
        { value: 'csv', label: 'CSV File', icon: FileText },
        { value: 'excel', label: 'Excel File', icon: FileSpreadsheet }
      ]
    },
    roster: {
      title: 'Export Shift Roster',
      description: 'Export shift schedules and assignments',
      icon: Clock,
      formats: [
        { value: 'csv', label: 'CSV File', icon: FileText },
        { value: 'excel', label: 'Excel File', icon: FileSpreadsheet }
      ]
    },
    timesheets: {
      title: 'Export Timesheets',
      description: 'Export timesheet data and approvals',
      icon: CalendarIcon,
      formats: [
        { value: 'pdf', label: 'PDF Report', icon: FileText }
      ]
    },
    analytics: {
      title: 'Export Analytics',
      description: 'Export dashboard analytics and reports',
      icon: BarChart3,
      formats: [
        { value: 'pdf', label: 'PDF Report', icon: FileText }
      ]
    }
  };

  const currentOption = exportOptions[exportType] || exportOptions.employees;

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
    const now = new Date();
    let start, end;
    
    switch (period) {
      case 'week':
        start = subDays(now, 7);
        end = now;
        break;
      case 'month':
        start = startOfMonth(now);
        end = endOfMonth(now);
        break;
      case 'quarter':
        start = subDays(now, 90);
        end = now;
        break;
      case 'year':
        start = subDays(now, 365);
        end = now;
        break;
      default:
        start = startOfMonth(now);
        end = endOfMonth(now);
    }
    
    setDateRange({
      start: format(start, 'yyyy-MM-dd'),
      end: format(end, 'yyyy-MM-dd')
    });
  };

  const handleExport = async () => {
    setIsExporting(true);
    setExportStatus(null);
    
    try {
      let url = '';
      let params = new URLSearchParams();
      
      // Add date range for time-based exports
      if (exportType === 'roster' || exportType === 'timesheets' || exportType === 'analytics') {
        params.append('start_date', dateRange.start);
        params.append('end_date', dateRange.end);
      }
      
      // Construct API endpoint
      switch (exportType) {
        case 'employees':
          url = `/api/export/employees/${selectedFormat}`;
          break;
        case 'roster':
          url = `/api/export/roster/${selectedFormat}`;
          break;
        case 'timesheets':
          url = `/api/export/timesheets/${selectedFormat}`;
          break;
        case 'analytics':
          url = `/api/export/analytics/${selectedFormat}`;
          break;
        default:
          throw new Error('Invalid export type');
      }
      
      // Add query parameters
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      // Trigger download
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      // Get filename from response headers or generate one
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `${exportType}_export_${format(new Date(), 'yyyyMMdd_HHmmss')}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      } else {
        // Add appropriate extension
        const extension = selectedFormat === 'excel' ? '.xlsx' : selectedFormat === 'pdf' ? '.pdf' : '.csv';
        filename += extension;
      }
      
      // Create blob and download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
      setExportStatus({ type: 'success', message: 'Export completed successfully!' });
      
      // Auto-close after success
      setTimeout(() => {
        onClose();
        setExportStatus(null);
      }, 2000);
      
    } catch (error) {
      setExportStatus({ type: 'error', message: error.message || 'Export failed. Please try again.' });
    } finally {
      setIsExporting(false);
    }
  };

  const IconComponent = currentOption.icon;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <IconComponent className="h-5 w-5 mr-2" />
            {currentOption.title}
          </DialogTitle>
          <DialogDescription>
            {currentOption.description}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Format Selection */}
          <div>
            <label className="text-sm font-medium mb-2 block">Export Format</label>
            <div className="grid grid-cols-1 gap-2">
              {currentOption.formats.map((format) => {
                const FormatIcon = format.icon;
                return (
                  <button
                    key={format.value}
                    onClick={() => setSelectedFormat(format.value)}
                    className={`flex items-center p-3 border rounded-lg transition-colors ${
                      selectedFormat === format.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <FormatIcon className="h-5 w-5 mr-3" />
                    <span className="font-medium">{format.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* Date Range Selection for time-based exports */}
          {(exportType === 'roster' || exportType === 'timesheets' || exportType === 'analytics') && (
            <div>
              <label className="text-sm font-medium mb-2 block">Date Range</label>
              <Select value={selectedPeriod} onValueChange={handlePeriodChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Last 7 Days</SelectItem>
                  <SelectItem value="month">This Month</SelectItem>
                  <SelectItem value="quarter">Last 3 Months</SelectItem>
                  <SelectItem value="year">Last Year</SelectItem>
                </SelectContent>
              </Select>
              
              <div className="mt-2 text-xs text-gray-500">
                {dateRange.start} to {dateRange.end}
              </div>
            </div>
          )}
          
          {/* Export Status */}
          {exportStatus && (
            <Alert variant={exportStatus.type === 'error' ? 'destructive' : 'default'}>
              {exportStatus.type === 'success' ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertDescription>{exportStatus.message}</AlertDescription>
            </Alert>
          )}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={isExporting}>
            {isExporting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Exporting...
              </>
            ) : (
              <>
                <Download className="h-4 w-4 mr-2" />
                Export
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

