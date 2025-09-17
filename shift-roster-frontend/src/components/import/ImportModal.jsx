import React, { useState, useRef } from 'react';
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
  Upload, 
  FileText, 
  FileSpreadsheet,
  Download,
  Users,
  AlertCircle,
  CheckCircle,
  Info,
  X
} from 'lucide-react';

export function ImportModal({ isOpen, onClose, importType = 'employees', onImportComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [step, setStep] = useState('select'); // 'select', 'validate', 'import', 'complete'
  const fileInputRef = useRef(null);

  const importOptions = {
    employees: {
      title: 'Import Employees',
      description: 'Import employee data from CSV or Excel files',
      icon: Users,
      templateEndpoint: '/api/export/templates/employees',
      validateEndpoint: '/api/import/employees/validate',
      importEndpoint: '/api/import/employees/csv',
      acceptedFormats: '.csv,.xlsx,.xls',
      sampleColumns: ['Employee ID', 'Name', 'Surname', 'Email', 'Contact Number', 'Role', 'Area of Responsibility', 'Skills']
    }
  };

  const currentOption = importOptions[importType] || importOptions.employees;

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setValidationResult(null);
      setImportResult(null);
      setStep('select');
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setValidationResult(null);
      setImportResult(null);
      setStep('select');
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch(currentOption.templateEndpoint, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to download template');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${importType}_import_template.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
    } catch (error) {
      console.error('Template download failed:', error);
    }
  };

  const validateFile = async () => {
    if (!selectedFile) return;
    
    setIsValidating(true);
    setValidationResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch(currentOption.validateEndpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'Validation failed');
      }
      
      setValidationResult(result);
      setStep('validate');
      
    } catch (error) {
      setValidationResult({
        valid: false,
        error: error.message || 'Validation failed. Please try again.'
      });
    } finally {
      setIsValidating(false);
    }
  };

  const performImport = async () => {
    if (!selectedFile || !validationResult?.valid) return;
    
    setIsImporting(true);
    setImportResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch(currentOption.importEndpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'Import failed');
      }
      
      setImportResult(result);
      setStep('complete');
      
      // Notify parent component
      if (onImportComplete) {
        onImportComplete(result);
      }
      
    } catch (error) {
      setImportResult({
        success: false,
        error: error.message || 'Import failed. Please try again.'
      });
    } finally {
      setIsImporting(false);
    }
  };

  const resetModal = () => {
    setSelectedFile(null);
    setValidationResult(null);
    setImportResult(null);
    setStep('select');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    resetModal();
    onClose();
  };

  const IconComponent = currentOption.icon;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
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
          {/* Step 1: File Selection */}
          {step === 'select' && (
            <>
              {/* Template Download */}
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">Download Template</h4>
                      <p className="text-sm text-gray-500">
                        Get the CSV template with sample data and required columns
                      </p>
                    </div>
                    <Button variant="outline" onClick={downloadTemplate}>
                      <Download className="h-4 w-4 mr-2" />
                      Template
                    </Button>
                  </div>
                </CardContent>
              </Card>
              
              {/* File Upload Area */}
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium mb-2">
                  {selectedFile ? selectedFile.name : 'Drop your file here or click to browse'}
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  Supports CSV and Excel files ({currentOption.acceptedFormats})
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={currentOption.acceptedFormats}
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Choose File
                </Button>
              </div>
              
              {/* Required Columns Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Required Columns</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="flex flex-wrap gap-2">
                    {currentOption.sampleColumns.map((column) => (
                      <Badge key={column} variant="outline">
                        {column}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
          
          {/* Step 2: Validation Results */}
          {step === 'validate' && validationResult && (
            <div className="space-y-4">
              <Alert variant={validationResult.valid ? 'default' : 'destructive'}>
                {validationResult.valid ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>
                  {validationResult.valid
                    ? `File validation successful! Found ${validationResult.total_rows} rows to import.`
                    : validationResult.error || 'File validation failed.'
                  }
                </AlertDescription>
              </Alert>
              
              {validationResult.valid && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Validation Summary</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 pt-0 space-y-2">
                    <div className="flex justify-between">
                      <span>Total Rows:</span>
                      <Badge>{validationResult.total_rows}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Columns Found:</span>
                      <Badge variant="outline">{validationResult.available_columns?.length || 0}</Badge>
                    </div>
                    
                    {validationResult.warnings && validationResult.warnings.length > 0 && (
                      <div className="mt-4">
                        <h5 className="font-medium text-sm mb-2">Warnings:</h5>
                        <div className="space-y-1">
                          {validationResult.warnings.map((warning, index) => (
                            <Alert key={index} variant="default">
                              <Info className="h-4 w-4" />
                              <AlertDescription className="text-xs">
                                {warning}
                              </AlertDescription>
                            </Alert>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
              
              {validationResult.missing_columns && validationResult.missing_columns.length > 0 && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Missing required columns: {validationResult.missing_columns.join(', ')}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}
          
          {/* Step 3: Import Results */}
          {step === 'complete' && importResult && (
            <div className="space-y-4">
              <Alert variant={importResult.success !== false ? 'default' : 'destructive'}>
                {importResult.success !== false ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <AlertDescription>
                  {importResult.success !== false
                    ? importResult.message || 'Import completed successfully!'
                    : importResult.error || 'Import failed.'
                  }
                </AlertDescription>
              </Alert>
              
              {importResult.imported_count !== undefined && (
                <Card>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">Records Imported:</span>
                      <Badge className="bg-green-100 text-green-800">
                        {importResult.imported_count}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              )}
              
              {importResult.errors && importResult.errors.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm text-red-600">Import Errors</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <div className="max-h-32 overflow-y-auto space-y-1">
                      {importResult.errors.slice(0, 10).map((error, index) => (
                        <div key={index} className="text-xs text-red-600 bg-red-50 p-2 rounded">
                          {error}
                        </div>
                      ))}
                      {importResult.errors.length > 10 && (
                        <div className="text-xs text-gray-500">
                          ... and {importResult.errors.length - 10} more errors
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            {step === 'complete' ? 'Close' : 'Cancel'}
          </Button>
          
          {step === 'select' && selectedFile && (
            <Button onClick={validateFile} disabled={isValidating}>
              {isValidating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Validating...
                </>
              ) : (
                'Validate File'
              )}
            </Button>
          )}
          
          {step === 'validate' && validationResult?.valid && (
            <Button onClick={performImport} disabled={isImporting}>
              {isImporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Importing...
                </>
              ) : (
                'Import Data'
              )}
            </Button>
          )}
          
          {step === 'validate' && !validationResult?.valid && (
            <Button variant="outline" onClick={() => setStep('select')}>
              Choose Different File
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

