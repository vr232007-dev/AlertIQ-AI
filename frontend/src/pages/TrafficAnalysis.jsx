
import React, { useRef, useState } from 'react';
import {
  FileText,
  UploadCloud,
  X,
  ShieldCheck,
  AlertTriangle,
  Activity,
  Loader2,
  FileSpreadsheet,
  Trash2,
  Eye,
  CheckCircle,
  XCircle
} from 'lucide-react';

import { uploadMultipleTrafficCsv } from '../api';

export function TrafficAnalysis({
  onInspectRecord,
  onAnalysisComplete
}) {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef(null);

  // Add selected CSV files
  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files || []);

    const validFiles = selectedFiles.filter((file) =>
      file.name.toLowerCase().endsWith('.csv')
    );

    if (validFiles.length !== selectedFiles.length) {
      setErrorMessage('Only CSV files are supported. Invalid files were ignored.');
    } else {
      setErrorMessage('');
    }

    setFiles((previousFiles) => {
      const combined = [...previousFiles, ...validFiles];

      // Avoid adding the same file twice
      return combined.filter((file, index, array) =>
        array.findIndex(
          (item) =>
            item.name === file.name &&
            item.size === file.size &&
            item.lastModified === file.lastModified
        ) === index
      );
    });

    setUploadResult(null);

    // Allows selecting the same file again later
    event.target.value = '';
  };

  // Handle drag and drop
  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragOver(false);

    const droppedFiles = Array.from(event.dataTransfer.files || []);

    const validFiles = droppedFiles.filter((file) =>
      file.name.toLowerCase().endsWith('.csv')
    );

    if (validFiles.length !== droppedFiles.length) {
      setErrorMessage('Only CSV files are supported. Invalid files were ignored.');
    } else {
      setErrorMessage('');
    }

    setFiles((previousFiles) => {
      const combined = [...previousFiles, ...validFiles];

      return combined.filter((file, index, array) =>
        array.findIndex(
          (item) =>
            item.name === file.name &&
            item.size === file.size &&
            item.lastModified === file.lastModified
        ) === index
      );
    });

    setUploadResult(null);
  };

  // Remove one selected file
  const handleRemoveFile = (indexToRemove) => {
    setFiles((previousFiles) =>
      previousFiles.filter((_, index) => index !== indexToRemove)
    );

    setUploadResult(null);
    setErrorMessage('');
  };

  // Remove all selected files
  const handleResetUpload = () => {
    setFiles([]);
    setUploadResult(null);
    setErrorMessage('');

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Upload and analyse all selected CSV files
  const handleUploadAndAnalyze = async () => {
    if (files.length === 0) {
      setErrorMessage('Please select at least one CSV file.');
      return;
    }

    setIsUploading(true);
    setErrorMessage('');
    setUploadResult(null);

    try {
      const data = await uploadMultipleTrafficCsv(files);

      setUploadResult(data);

      if (data.failed_files?.length > 0) {
        const failureMessage = data.failed_files
          .map((item) => `${item.filename}: ${item.reason}`)
          .join('\n');

        setErrorMessage(failureMessage);
      }

      if (data.successful_files?.length > 0 && onAnalysisComplete) {
        onAnalysisComplete();
      }
    } catch (error) {
      setErrorMessage(
        error.message || 'An error occurred while analysing the CSV files.'
      );
    } finally {
      setIsUploading(false);
    }
  };

  const summary = uploadResult?.summary;

  const getPercentage = (value, total) => {
    if (!total) return '0.0';
    return ((value / total) * 100).toFixed(1);
  };

  const formatProbability = (value) => {
    const probability = Number(value || 0);
    return `${(probability * 100).toFixed(1)}%`;
  };

  return (
    <div className="space-y-6 text-white">

      {/* Page heading */}
      <div>
        <h1 className="text-2xl font-bold">
          Traffic Analysis
        </h1>

        <p className="text-sm text-slate-400 mt-2">
          Upload multiple network traffic CSV files and analyse them
          using the AlertIQ AI intrusion detection model.
        </p>
      </div>

      {/* Upload section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">

        <div className="flex items-center gap-3 mb-5">
          <div className="p-3 bg-cyan-500/10 rounded-lg">
            <UploadCloud className="w-6 h-6 text-cyan-400" />
          </div>

          <div>
            <h2 className="font-semibold text-lg">
              Upload Network Traffic Files
            </h2>

            <p className="text-xs text-slate-400">
              Select multiple separate CSV files for batch analysis.
            </p>
          </div>
        </div>

        {/* Drag and drop area */}
        <div
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
            isDragOver
              ? 'border-cyan-400 bg-cyan-500/10'
              : 'border-slate-700 hover:border-cyan-500'
          }`}
        >
          <FileSpreadsheet className="w-12 h-12 text-cyan-400 mx-auto mb-4" />

          <h3 className="font-semibold text-white">
            Drag and drop your CSV files here
          </h3>

          <p className="text-xs text-slate-400 mt-2 mb-5">
            You can select multiple files at the same time.
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,text/csv"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="csv-upload-input"
          />

          <label
            htmlFor="csv-upload-input"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-semibold cursor-pointer transition-colors"
          >
            <UploadCloud className="w-4 h-4" />
            Choose Multiple CSV Files
          </label>

          <p className="text-xs text-slate-500 mt-4">
            Supported format: .csv
          </p>
        </div>

        {/* Selected files */}
        {files.length > 0 && (
          <div className="mt-6 space-y-3">

            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm">
                Selected Files ({files.length})
              </h3>

              <button
                onClick={handleResetUpload}
                disabled={isUploading}
                className="text-xs text-red-400 hover:text-red-300 disabled:opacity-50"
              >
                Remove All
              </button>
            </div>

            {files.map((file, index) => (
              <div
                key={`${file.name}-${file.lastModified}-${index}`}
                className="flex items-center justify-between gap-3 p-3 rounded-lg bg-slate-950 border border-slate-800"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <FileText className="w-5 h-5 text-cyan-400 shrink-0" />

                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">
                      {file.name}
                    </p>

                    <p className="text-xs text-slate-400">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleRemoveFile(index)}
                  disabled={isUploading}
                  className="text-slate-400 hover:text-red-400 disabled:opacity-50"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}

            {/* Upload button */}
            <button
              onClick={handleUploadAndAnalyze}
              disabled={files.length === 0 || isUploading}
              className="w-full flex items-center justify-center gap-2 p-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold text-sm transition-colors"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analysing CSV Files...
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5" />
                  Upload and Analyse {files.length} File(s)
                </>
              )}
            </button>
          </div>
        )}

        {/* Error and failed file messages */}
        {errorMessage && (
          <div className="mt-5 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />

              <div>
                <p className="font-semibold text-sm text-red-400">
                  Analysis Notice
                </p>

                <pre className="text-xs text-red-300 whitespace-pre-wrap mt-1 font-sans">
                  {errorMessage}
                </pre>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Combined analysis summary */}
      {summary && (
        <div className="space-y-5">

          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />

            <h2 className="text-lg font-bold">
              Combined Analysis Results
            </h2>
          </div>

          <p className="text-xs text-slate-400">
            Successfully processed:{' '}
            {uploadResult.successful_files?.join(', ') || 'No files'}
          </p>

          {/* Summary cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-400">
                  Total Analysed
                </p>

                <Activity className="w-5 h-5 text-cyan-400" />
              </div>

              <p className="text-3xl font-bold mt-3">
                {summary.total_analyzed ?? 0}
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-400">
                  Benign Traffic
                </p>

                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>

              <p className="text-3xl font-bold text-emerald-400 mt-3">
                {summary.benign_count ?? 0}
              </p>

              <p className="text-xs text-slate-400 mt-1">
                {getPercentage(
                  summary.benign_count,
                  summary.total_analyzed
                )}% of analysed traffic
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-400">
                  Attack Traffic
                </p>

                <AlertTriangle className="w-5 h-5 text-red-400" />
              </div>

              <p className="text-3xl font-bold text-red-400 mt-3">
                {summary.attack_count ?? 0}
              </p>

              <p className="text-xs text-slate-400 mt-1">
                {getPercentage(
                  summary.attack_count,
                  summary.total_analyzed
                )}% of analysed traffic
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-400">
                  Alerts Generated
                </p>

                <AlertTriangle className="w-5 h-5 text-amber-400" />
              </div>

              <p className="text-3xl font-bold text-amber-400 mt-3">
                {summary.alerts_created ?? 0}
              </p>
            </div>

          </div>

          {/* File processing report */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="font-semibold mb-4">
              File Processing Report
            </h3>

            <div className="space-y-3">

              {uploadResult.successful_files?.map((filename, index) => (
                <div
                  key={`success-${index}`}
                  className="flex items-center gap-3 text-sm"
                >
                  <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />

                  <span className="text-slate-300 break-all">
                    {filename}
                  </span>

                  <span className="text-emerald-400 text-xs ml-auto">
                    Successful
                  </span>
                </div>
              ))}

              {uploadResult.failed_files?.map((item, index) => (
                <div
                  key={`failed-${index}`}
                  className="flex items-start gap-3 text-sm"
                >
                  <XCircle className="w-4 h-4 text-red-400 shrink-0" />

                  <div className="min-w-0">
                    <p className="text-slate-300 break-all">
                      {item.filename}
                    </p>

                    <p className="text-xs text-red-400 mt-1">
                      {item.reason}
                    </p>
                  </div>

                  <span className="text-red-400 text-xs ml-auto">
                    Failed
                  </span>
                </div>
              ))}

            </div>
          </div>

          {/* Prediction results table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">

            <div className="p-5 border-b border-slate-800">
              <h3 className="font-semibold">
                Individual Traffic Predictions
              </h3>

              <p className="text-xs text-slate-400 mt-1">
                Showing the available prediction preview from the uploaded files.
              </p>
            </div>

            {uploadResult.results?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">

                  <thead className="bg-slate-950 text-slate-400 text-xs uppercase">
                    <tr>
                      <th className="px-4 py-3">#</th>
                      <th className="px-4 py-3">Source File</th>
                      <th className="px-4 py-3">Classification</th>
                      <th className="px-4 py-3">Attack Probability</th>
                      <th className="px-4 py-3">Destination Port</th>
                      <th className="px-4 py-3">Total Packets</th>
                      <th className="px-4 py-3">Action</th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-800">

                    {uploadResult.results.map((row, index) => (
                      <tr
                        key={`${row.source_filename || 'file'}-${row.row_index || index}`}
                        className="hover:bg-slate-800/50"
                      >
                        <td className="px-4 py-3 text-slate-400">
                          {row.row_index ?? index + 1}
                        </td>

                        <td className="px-4 py-3 text-slate-300">
                          <span className="block max-w-40 truncate">
                            {row.source_filename || 'CSV file'}
                          </span>
                        </td>

                        <td className="px-4 py-3">
                          {row.predicted_class === 'ATTACK' ? (
                            <span className="px-2 py-1 rounded-md bg-red-500/10 text-red-400 text-xs font-semibold">
                              ATTACK
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
                              BENIGN
                            </span>
                          )}
                        </td>

                        <td className="px-4 py-3 text-slate-300">
                          {formatProbability(row.attack_probability)}
                        </td>

                        <td className="px-4 py-3 text-slate-300">
                          {row.destination_port ?? '-'}
                        </td>

                        <td className="px-4 py-3 text-slate-300">
                          {row.total_packets ?? '-'}
                        </td>

                        <td className="px-4 py-3">
                          {onInspectRecord && (
                            <button
                              onClick={() => onInspectRecord(row.row_index)}
                              className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 text-xs"
                            >
                              <Eye className="w-4 h-4" />
                              Inspect
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}

                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400 text-sm">
                No prediction records are available to display.
              </div>
            )}

            {uploadResult.has_more && (
              <div className="p-4 border-t border-slate-800 text-center text-xs text-slate-400">
                Showing a preview of the results. Additional records may be available in the analysis history.
              </div>
            )}

          </div>

        </div>
      )}
    </div>
  );
}

export default TrafficAnalysis;
