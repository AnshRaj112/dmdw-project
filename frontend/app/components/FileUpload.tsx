'use client';

import { useCallback, useState } from 'react';
import { useDropzone, type FileRejection } from 'react-dropzone';
import { Upload, File, X, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, selectedFile }) => {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError('File size must be less than 10MB');
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Please upload a PDF or DOC file');
      } else {
        setError('Invalid file type. Please upload a PDF or DOC file.');
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  });

  const removeFile = () => {
    onFileSelect(null);
    setError(null);
  };

  return (
    <div className="file-upload">
      <div
        {...getRootProps()}
        className={`file-upload__dropzone ${
          isDragActive ? 'file-upload__dropzone--active' : ''
        } ${error ? 'file-upload__dropzone--error' : ''}`}
      >
        <input {...getInputProps()} />
        
        {selectedFile ? (
          <div className="file-upload__file-info">
            <div className="flex items-center justify-center mb-2">
              <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
              <span className="font-medium text-green-700">File uploaded successfully!</span>
            </div>
            <div className="flex items-center justify-center">
              <File className="w-4 h-4 mr-2" />
              <span className="text-sm">{selectedFile.name}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
                className="ml-2 text-red-600 hover:text-red-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div>
            <Upload className="file-upload__icon" />
            <p className="file-upload__text">
              {isDragActive
                ? 'Drop your resume here...'
                : 'Drag & drop your resume here, or click to select'}
            </p>
            <p className="file-upload__hint">
              Supports PDF, DOC, and DOCX files up to 10MB
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="error mt-4">
          <h3 className="error__title">Upload Error</h3>
          <p className="error__message">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
