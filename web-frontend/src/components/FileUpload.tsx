import React, { useState, ChangeEvent } from 'react';
import Button from './Button';

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  acceptedFileTypes?: string;
  multiple?: boolean;
  label?: string;
  buttonText?: string;
  className?: string;
  isLoading?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  acceptedFileTypes = '.csv',
  multiple = false,
  label = '上传健康数据文件',
  buttonText = '上传',
  className = '',
  isLoading = false,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
      setUploadStatus('idle');
      setStatusMessage('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('error');
      setStatusMessage('请选择一个文件上传');
      return;
    }

    try {
      setUploadStatus('idle');
      setStatusMessage('正在上传...');
      
      await onUpload(selectedFile);
      
      setUploadStatus('success');
      setStatusMessage('上传成功!');
      setSelectedFile(null);

      // 重置input
      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error) {
      console.error('文件上传失败', error);
      setUploadStatus('error');
      setStatusMessage('上传失败，请重试');
    }
  };

  return (
    <div className={`flex flex-col space-y-4 ${className}`}>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      
      <div className="flex flex-col space-y-3">
        <div className="flex items-center">
          <input
            id="file-upload"
            type="file"
            accept={acceptedFileTypes}
            multiple={multiple}
            onChange={handleFileChange}
            disabled={isLoading}
            className="sr-only"
          />
          <label
            htmlFor="file-upload"
            className={`cursor-pointer py-2 px-4 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors mr-3 flex-grow ${
              isLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {selectedFile ? selectedFile.name : '选择文件'}
          </label>
          
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || isLoading}
            isLoading={isLoading}
            variant="primary"
            className="whitespace-nowrap"
          >
            {isLoading ? '上传中...' : buttonText}
          </Button>
        </div>
        
        {uploadStatus === 'success' && (
          <div className="text-sm py-2 px-3 bg-green-50 text-green-700 rounded-md">
            {statusMessage}
          </div>
        )}
        
        {uploadStatus === 'error' && (
          <div className="text-sm py-2 px-3 bg-red-50 text-red-700 rounded-md">
            {statusMessage}
          </div>
        )}
        
        {uploadStatus === 'idle' && statusMessage && (
          <div className="text-sm py-2 px-3 bg-gray-50 text-gray-700 rounded-md">
            {statusMessage}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload; 